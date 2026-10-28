"""Design-only path learning, nominal calibration, hard-cap exploratory pilots."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import argparse,time,json
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from data import ROOT,DATA,load,save
from index import IVF,full_topk,distances
from fresh import calibration_queries
from control import *
CAPS=[.10,.25,.50,1.00];BOOT={}
def ci(v):
    if len(v)==0:return [None,None]
    if len(v) not in BOOT:
        # Exact bootstrap count distribution; compact storage avoids retaining
        # a large float64 matrix for every group size over all seeds.
        BOOT[len(v)]=np.random.default_rng(123).multinomial(len(v),np.full(len(v),1/len(v)),size=2000).astype(np.uint16)
    return np.quantile(BOOT[len(v)]@v/len(v),[.025,.975]).tolist()
def smoke():
    rng=np.random.default_rng(10);base=rng.normal(size=(110,5)).astype('f');q=rng.normal(size=(80,5)).astype('f')
    index=IVF(8,1);index.build(base);_,truth=full_topk(q,base);l,w=index.curves(q,truth)
    _,blocked=full_topk(q,base,block=7,corpus_block=23)
    assert np.array_equal(blocked,np.argsort(distances(q,base),axis=1,kind='stable')[:,:10])
    assert np.allclose(distances(np.r_[q,q],base),np.r_[distances(q,base),distances(q,base)])
    # Use physical counts in a tiny eight-list positive control.
    l=np.c_[np.ones(len(l)),l];w=np.c_[np.zeros(len(w),dtype=int),w]+64
    for cap in [64,90,174]:
        p=max_prefix(w,cap);assert np.all(w[np.arange(80),p]<=cap)
        for lower in range(9):
            chosen=np.minimum(p,lower);assert np.all(l[np.arange(80),chosen]>=l[np.arange(80),p]-1e-12)
    group=np.ones((80,15),dtype=bool)
    assert np.all(test_values(np.zeros(80),group)[0]<.025)
    fake_l=np.c_[np.ones(100),np.ones((100,63)),np.zeros(100)]
    fake_w=np.broadcast_to(np.arange(65)+64,(100,65))
    witness=infeasibility(fake_l,fake_w,np.ones((100,15),dtype=bool),100)
    assert witness['rejected']
    cell=np.arange(100)%10;pol=np.full(10,64);path=uniform_path()
    selected,status=select(path,fake_l,fake_w,np.ones((100,15),dtype=bool),cell,128)
    assert status['status']=='nominal_certified' and np.all(selected==64)
    # A rare group cannot be certified from zero catastrophes alone.
    assert np.exp(71*np.log(.95))>.025 and np.exp(72*np.log(.95))<=.025
    train_loss=np.maximum(0,1-np.arange(65)[None,:]/30)*np.ones((100,1))
    train_work=np.broadcast_to(np.arange(65)+64,(100,65))
    learned=repair_path(train_loss,train_work,np.ones((100,15),dtype=bool),cell,120)
    assert np.all(np.diff(learned,axis=0)>=0) and np.all(learned[-1]==64)
    save(ROOT/'smoke.json',dict(passed=True,checks=['hard-cap count compliance including zero-prefix',
        'pointwise prefix risk floor','known infeasible-cap positive control','fixed-sequence safe-anchor control',
        '72-sample tail-test threshold','nested greedy path'],final_queries_evaluated=False))
    print('Smoke passed',flush=True)
def run(name,seed,data):
    BOOT.clear()
    started=time.perf_counter();base,dq,old_cal,pq,prov=load(name,seed,data)
    cq,fresh_ids=calibration_queries(name,seed,data,prov['corpus_ids'])
    prov['previous_calibration_ids_not_used']=prov.pop('calibration_ids')
    prov['calibration_training_ids']=fresh_ids.tolist();prov['calibration_source']='train_vectors_excluding_corpus'
    idx=IVF(64,seed);build=idx.build(base)
    dc=distances(dq,idx.centers);cc=distances(cq,idx.centers);pc=distances(pq,idx.centers)
    da,dd=features(dc);edges=np.quantile(da,np.arange(.1,1,.1));median=float(np.median(dd))
    dg,ds,dec_d=groups_and_cells(dc,edges,median);cg,cs,dec_c=groups_and_cells(cc,edges,median);pg,ps,dec_p=groups_and_cells(pc,edges,median)
    curves=[];label_t=time.perf_counter()
    for q in [dq,cq,pq]:
        _,truth=full_topk(q,base);loss,work=idx.curves(q,truth);curves.append(add_zero(loss,work))
    (dl,dw),(cl,cw),(pl,pw)=curves;label_seconds=time.perf_counter()-label_t
    uniform=uniform_path();template=template_path(dl,ds);group_ref=np.array([crc(cl[dec_c==g]) for g in range(10)])
    metrics=[];risktable=[];paired=[];paths_meta=[];sample_ablation=[];raw={};all_policies={};issued={}
    for fraction in CAPS:
        cap=64+int(fraction*len(base));cpmax=max_prefix(cw,cap);ppmax=max_prefix(pw,cap)
        train_t=time.perf_counter()
        paths={'overlap_repair':repair_path(dl,dw,dg,ds,cap),
               'no_overlap':repair_path(dl,dw,dg,ds,cap,'no_overlap'),
               'no_tail':repair_path(dl,dw,dg,ds,cap,'no_tail'),
               'uniform_ltt':uniform,'cell_shift_ltt':template,'cap_max':np.full((1,10),64)}
        path_seconds=time.perf_counter()-train_t
        floor=pl[np.arange(600),ppmax];fr,fn=risks(floor,pg)
        floor_violations=int(((fr>TARGET+1e-12)&(fn[:,None]>0)).sum())
        for method in list(paths)+['group_crc_uncapped','group_crc_capped']:
            calibration_t=time.perf_counter()
            if method in paths:
                policy,state=select(paths[method],cl,cw,cg,cs,cap);real=policy is not None
                diagnostic=policy if real else np.full(10,64);cell_ids=ps;limit=ppmax
                paths_meta.append(dict(cap_fraction=fraction,method=method,length=len(paths[method]),path=paths[method].tolist()))
                small_policy,small_state=select(paths[method],cl[:1000],cw[:1000],cg[:1000],cs[:1000],cap)
                sample_ablation.append(dict(dataset=name,seed=seed,cap_fraction=fraction,method=method,ncal=1000,
                    min_group_count=int(cg[:1000].sum(0).min()),status=small_state['status']))
                sample_ablation.append(dict(dataset=name,seed=seed,cap_fraction=fraction,method=method,ncal=5000,
                    min_group_count=int(cg.sum(0).min()),status=state['status']))
            else:
                diagnostic=group_ref;cell_ids=dec_p;limit=np.full(600,64) if method=='group_crc_uncapped' else ppmax
                state=dict(status='uncertified_reference',tests=0,witness=None);real=False;policy=group_ref
            calibration_seconds=time.perf_counter()-calibration_t
            v,w,p=evaluate(pl,pw,diagnostic,cell_ids,limit);z,n=risks(v,pg)
            violations=int(((z>TARGET+1e-12)&(n[:,None]>0)).sum())
            key=f'{fraction}__{method}';raw[key+'__loss']=v;raw[key+'__work']=w;raw[key+'__prefix']=p
            all_policies[key]=diagnostic.tolist();issued[key]=bool(real)
            lo,hi=ci(v);active=state['status']=='nominal_certified'
            metrics.append(dict(dataset=name,seed=seed,cap_fraction=fraction,cap=cap,method=method,status=state['status'],
                diagnostic_only=not active,nominal_issued=active,mean_fnr=float(v.mean()),fnr_ci_low=lo,fnr_ci_high=hi,
                cvar90=empirical_cvar(v),mean_distances=float(w.mean()),max_distances=int(w.max()),cap_violation_count=int((w>cap).sum()),
                empirical_constraint_violations=violations,observed_constraint_count=int((n>0).sum()*3),
                pilot_floor_constraint_violations=floor_violations,finite_pilot_infeasible=bool(floor_violations>0),
                min_calibration_group_count=int(cg.sum(0).min()),path_learning_seconds=path_seconds,
                calibration_selection_seconds=calibration_seconds,tests=state['tests'],last_joint_pvalue=state.get('last_joint_pvalue'),
                witness=state.get('witness')))
            for g,gname in enumerate(GROUP_NAMES):
                take=pg[:,g];vals=components(v[take]);ints=[ci(vals[:,s]) for s in range(3)]
                risktable.append(dict(dataset=name,seed=seed,cap_fraction=fraction,method=method,status=state['status'],group=gname,n=int(n[g]),
                    mean_fnr=float(z[g,0]) if n[g] else None,mean_ci_low=ints[0][0],mean_ci_high=ints[0][1],
                    tail20=float(z[g,1]) if n[g] else None,tail20_ci_low=ints[1][0],tail20_ci_high=ints[1][1],
                    tail50=float(z[g,2]) if n[g] else None,tail50_ci_low=ints[2][0],tail50_ci_high=ints[2][1],
                    empirical_cvar90=empirical_cvar(v[take])))
        for method in ['uniform_ltt','cell_shift_ltt','no_overlap','no_tail']:
            a=f'{fraction}__overlap_repair';b=f'{fraction}__{method}';diff=raw[a+'__work']-raw[b+'__work'];lo,hi=ci(diff)
            paired.append(dict(dataset=name,seed=seed,cap_fraction=fraction,comparison=method,
                both_nominally_issued=issued[a] and issued[b],mean_difference=float(diff.mean()),ci_low=lo,ci_high=hi,
                work_ratio=float(raw[a+'__work'].mean()/raw[b+'__work'].mean())))
    out=ROOT/'results';out.mkdir(exist_ok=True);prefix=f'{name}_{seed}'
    prov.update(ambiguity_edges=edges.tolist(),distance_median=median,calibration_group_counts=cg.sum(0).tolist(),group_names=GROUP_NAMES)
    raw.update(design_loss=dl,design_work=dw,calibration_loss=cl,calibration_work=cw,pilot_loss=pl,pilot_work=pw,
        design_groups=dg,calibration_groups=cg,pilot_groups=pg,design_cells=ds,calibration_cells=cs,pilot_cells=ps,pilot_deciles=dec_p)
    np.savez_compressed(out/(prefix+'_raw.npz'),**raw)
    save(out/(prefix+'_metrics.json'),dict(metrics=metrics,risks=risktable,paired=paired,paths=paths_meta,sample_ablation=sample_ablation,policies=all_policies,
        timing=dict(build_seconds=build,truth_curve_seconds=label_seconds,total_seconds=time.perf_counter()-started)))
    save(out/(prefix+'_provenance.json'),prov)
    print(name,seed,[(m['cap_fraction'],m['status'],round(m['mean_distances'])) for m in metrics if m['method']=='overlap_repair'],flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['smoke','pilot','full']);p.add_argument('--data',type=Path,default=DATA)
    p.add_argument('--datasets',nargs='+',default=['glove','fashion']);p.add_argument('--seeds',nargs='+',type=int,default=list(range(5)));a=p.parse_args()
    with threadpool_limits(limits=1):
        if a.action=='smoke':smoke();return
        if a.action=='full':raise SystemExit('Full stage pending novelty/gate clearance and independent calibration. No final queries accessed.')
        assert json.loads((ROOT/'smoke.json').read_text())['passed']
        for name in a.datasets:
            for seed in a.seeds:run(name,seed,a.data)
if __name__=='__main__':main()
