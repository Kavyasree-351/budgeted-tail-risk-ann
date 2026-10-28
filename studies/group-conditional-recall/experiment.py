"""Predeclared Direction-B exploratory pilots. No reserved query evaluation."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,time,json
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from data import ROOT,DATA,load,save
from index import IVF,distances,full_topk,stable_small_topk
from methods import crc,kl_crc,feature,bins,calibrate,budgets
COUNTS={}
def ci(v):
    if not len(v):return [None,None]
    if len(v) not in COUNTS:
        ix=np.random.default_rng(123).integers(len(v),size=(2000,len(v)))
        COUNTS[len(v)]=np.stack([np.bincount(row,minlength=len(v)) for row in ix]).astype(float)
    return np.quantile(COUNTS[len(v)]@v/len(v),[.025,.975]).tolist()
def smoke():
    rng=np.random.default_rng(3);x=rng.normal(size=(100,5)).astype('f');q=rng.normal(size=(15,5)).astype('f')
    index=IVF(8,0);index.build(x);_,truth=full_topk(q,x);loss,work=index.curves(q,truth)
    for p in range(1,9):
        found,count=index.search(q,x,p)
        actual=np.array([1-len(set(a)&set(b))/10 for a,b in zip(found,truth)])
        assert np.allclose(actual,loss[:,p-1]) and np.array_equal(count,work[:,p-1])
    assert crc(np.empty((0,64)))==63 and crc(np.zeros((5,64)))==63
    assert kl_crc(np.zeros((200,64)))==0
    assert np.array_equal(bins(np.array([0,.5,1]),np.array([.2,.8])),[0,1,2])
    # Positive control: CRC accepts global risk=.09 while group risk=.45.
    toy=np.zeros((100,64));toy[80:100,0]=.45
    assert np.isclose(toy[:,0].mean(),.09) and np.isclose(toy[80:,0].mean(),.45)
    assert crc(toy)==0 and crc(toy[80:100])==1
    assert np.all(np.maximum.accumulate([3,1,6,2])>=np.array([3,1,6,2]))
    frozen=np.quantile(np.arange(400),np.arange(.1,1,.1));before=frozen.copy()
    bins(np.array([-1e8,1e8]),frozen);assert np.array_equal(before,frozen)
    save(ROOT/'smoke.json',dict(passed=True,checks=['direct ANN vs trace all budgets','CRC empty/small-group safe fallback',
        'bounded-KL zero-loss control','frozen design bins and deterministic assignment',
        'marginal/subgroup analytic positive control','monotone policy domination','exact full search'],
        synthetic_positive_control=dict(global_fnr=.09,hard_fnr=.45,global_crc_accepts_one_probe=True,not_real_data=True)))
    print('Smoke passed',flush=True)
def run(name,seed,data):
    start=time.perf_counter();base,design,cal,pilot,prov=load(name,seed,data)
    index=IVF(64,seed);build=index.build(base)
    begin=time.perf_counter();dc=distances(design,index.centers);cc=distances(cal,index.centers);pc=distances(pilot,index.centers)
    coarse_seconds=time.perf_counter()-begin
    edges=np.quantile(feature(dc),np.arange(.1,1,.1));cg=bins(feature(cc),edges);pg=bins(feature(pc),edges)
    post_times=[]
    for _ in range(51):
        t=time.perf_counter();bins(feature(pc),edges);post_times.append(time.perf_counter()-t)
    feature_seconds=float(np.median(post_times))
    t=time.perf_counter();_,ct=full_topk(cal,base);cl,_=index.curves(cal,ct);label_seconds=time.perf_counter()-t
    _,pt=full_topk(pilot,base);pl,pw=index.curves(pilot,pt)
    held_cells=np.random.default_rng(seed+801).choice(64,13,replace=False)
    ch=np.isin(cc.argmin(1),held_cells);ph=np.isin(pc.argmin(1),held_cells)
    random_map=np.random.default_rng(seed+901).integers(0,10,10000)
    cr=random_map[prov['calibration_ids']];pr=random_map[prov['pilot_ids']]
    rows=[];policies=[];paired=[];raw={};fit_times={}
    for scenario in ['iid','heldout_cells']:
        mask=np.ones(1000,dtype=bool) if scenario=='iid' else ~ch
        assert scenario!='heldout_cells' or not np.any(ch[mask])
        t=time.perf_counter();fits=calibrate(cl[mask],cg[mask],ch[mask],cr[mask]);fit_seconds=time.perf_counter()-t
        fit_times[scenario]=fit_seconds
        groups={f'decile_{g+1}':pg==g for g in range(10)}
        groups.update(marginal=np.ones(600,dtype=bool),hard_9_10=pg>=8,held_cells=ph,seen_cells=~ph)
        v_by_method={};w_by_method={}
        for method,policy in fits.items():
            p=budgets(method,policy,pg,ph,pr,scenario=='heldout_cells')
            v=pl[np.arange(600),p];w=pw[np.arange(600),p]
            v_by_method[method]=v;w_by_method[method]=w
            key=scenario+'__'+method;raw[key+'__loss']=v;raw[key+'__corpus_distances']=w;raw[key+'__nprobe']=p+1
            policies.append(dict(dataset=name,seed=seed,scenario=scenario,method=method,budgets=(policy+1).tolist(),
                calibration_counts=np.bincount(cg[mask],minlength=10).tolist(),calibration_count=int(mask.sum()),
                calibration_ids_used=np.asarray(prov['calibration_ids'])[mask].tolist()))
            for scope,which in groups.items():
                z=v[which];lo,hi=ci(z)
                rows.append(dict(dataset=name,seed=seed,scenario=scenario,method=method,scope=scope,n=int(which.sum()),
                    fnr=float(z.mean()) if len(z) else None,ci_low=lo,ci_high=hi,
                    corpus_distances=float(w[which].mean()) if len(z) else None,
                    total_distances=float(w[which].mean()+(0 if method=='exact' else 64)) if len(z) else None,
                    mean_nprobe=float((p[which]+1).mean()) if len(z) else None))
        reference=w_by_method['global_crc']+64
        for method in fits:
            w=w_by_method[method]+(0 if method=='exact' else 64);diff=w-reference;lo,hi=ci(diff)
            means=[v_by_method[method][pg==g].mean() for g in range(10) if np.any(pg==g)]
            paired.append(dict(dataset=name,seed=seed,scenario=scenario,method=method,
                total_distance_ratio=float(w.mean()/reference.mean()),paired_work_difference=float(diff.mean()),
                paired_work_ci_low=lo,paired_work_ci_high=hi,empirical_decile_violation_fraction=float(np.mean(np.array(means)>.1))))
    raw.update(pilot_deciles=pg,pilot_held_cells=ph,calibration_deciles=cg,calibration_held_cells=ch,
        calibration_loss_curves=cl,pilot_loss_curves=pl,pilot_work_curves=pw,decile_edges=edges)
    prov.update(held_centroid_cells=held_cells.tolist(),decile_edges=edges.tolist())
    out=ROOT/'results';out.mkdir(exist_ok=True);prefix=f'{name}_{seed}'
    save(out/(prefix+'_metrics.json'),dict(rows=rows,policies=policies,paired=paired,timing=dict(build_seconds=build,
        calibration_truth_curve_seconds=label_seconds,coarse_all_queries_seconds=coarse_seconds,
        feature_lookup_600_queries_seconds=feature_seconds,policy_fit_seconds_by_scenario=fit_times,total_seconds=time.perf_counter()-start)))
    save(out/(prefix+'_provenance.json'),prov);np.savez_compressed(out/(prefix+'_raw.npz'),**raw)
    primary=[r for r in rows if r['scenario']=='iid' and r['method']=='global_crc' and r['scope'] in ['marginal','hard_9_10']]
    print(name,seed,[(r['scope'],round(r['fnr'],4),r['n']) for r in primary],flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['smoke','pilot','full']);p.add_argument('--data',type=Path,default=DATA)
    p.add_argument('--datasets',nargs='+',default=['glove','fashion'],choices=['glove','fashion']);p.add_argument('--seeds',nargs='+',type=int,default=list(range(5)));a=p.parse_args()
    with threadpool_limits(limits=1):
        if a.action=='smoke':smoke();return
        if a.action=='full':raise SystemExit('Full stage blocked: needs passed failure/efficiency gates, distinct novelty and frozen fresh-query protocol. Reserved queries not opened.')
        assert json.loads((ROOT/'smoke.json').read_text())['passed']
        for name in a.datasets:
            for seed in a.seeds:run(name,seed,a.data)
if __name__=='__main__':main()
