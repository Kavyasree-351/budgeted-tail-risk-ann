"""Controlled IVF feasibility pilot, not a reproduction of ConANN/DARTH."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[key]='1'
import argparse,csv,gzip,hashlib,json,platform,time,urllib.request
from pathlib import Path
import h5py
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT.parents[1]/'work'/'datasets'/'mpl-cache'))
KS=[1,10,50]; P=64; ALPHA=.1
def save(path,obj): path.write_text(json.dumps(obj,indent=2),encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def load(data,name):
    rng=np.random.default_rng(20261026)
    if name=='glove':
        file=data/'glove-25-angular.hdf5'
        with h5py.File(file) as f:
            ids=rng.permutation(len(f['test'])); used=ids[:2000]; ix=np.argsort(used)
            bi=np.sort(np.random.default_rng(923).choice(len(f['train']),20000,replace=False))
            base=np.asarray(f['train'][bi],dtype='f'); q=np.asarray(f['test'][used[ix]],dtype='f')[np.argsort(ix)]
        base/=np.maximum(np.linalg.norm(base,axis=1,keepdims=True),1e-12)
        q/=np.maximum(np.linalg.norm(q,axis=1,keepdims=True),1e-12)
        files={file.name:sha(file)}
    else:
        def images(file):
            with gzip.open(file,'rb') as f:
                header=np.frombuffer(f.read(16),dtype='>u4'); assert header[0]==2051
                return np.frombuffer(f.read(),dtype='u1').reshape(int(header[1]),-1)
        train=data/'train-images-idx3-ubyte.gz'; test=data/'t10k-images-idx3-ubyte.gz'
        # Decompression reads bytes but no reserved test vectors are processed or evaluated.
        # Raw image archive storage is contiguous; take split IDs before float conversion.
        raw=images(test); ids=rng.permutation(len(raw));used=ids[:2000]
        bi=np.sort(np.random.default_rng(923).choice(60000,10000,replace=False))
        base=images(train)[bi].astype('f')/255; q=raw[used].astype('f')/255
        files={x.name:sha(x) for x in [train,test]}
    assert len(set(used))==2000 and np.isfinite(q).all()
    return base,q,dict(files=files,base_size=len(base),dimension=base.shape[1],design_ids=used[:400].tolist(),
        calibration_ids=used[400:1400].tolist(),pilot_ids=used[1400:].tolist(),reserved_unevaluated_ids=ids[2000:].tolist(),
        base_ids_sha256=hashlib.sha256(bi.tobytes()).hexdigest())
def dist(q,x): return np.maximum((q*q).sum(1)[:,None]+(x*x).sum(1)[None,:]-2*q@x.T,0)
def trace(base,q,seed,nlist=P):
    t=time.perf_counter(); model=MiniBatchKMeans(n_clusters=nlist,random_state=seed,n_init=3,batch_size=1024,max_iter=100)
    labels=model.fit_predict(base); build=time.perf_counter()-t;t=time.perf_counter()
    coarse=dist(q,model.cluster_centers_); order=np.argsort(coarse,axis=1,kind='stable');rank=np.argsort(order,axis=1)
    work=np.cumsum(np.bincount(labels,minlength=nlist)[order],axis=1)
    loss=np.empty((len(q),3,nlist),dtype='f');zero=0
    for lo in range(0,len(q),64):
        d=dist(q[lo:lo+64],base); truth=np.argsort(d,axis=1,kind='stable')[:,:50]
        zero+=int((d.min(1)<=1e-8).sum())
        r=np.take_along_axis(rank[lo:lo+len(d)],labels[truth],axis=1)
        for j,k in enumerate(KS):loss[lo:lo+len(d),j]=1-(r[:,:k,None]<=np.arange(nlist)).mean(1)
    c=np.take_along_axis(coarse,order,axis=1);feature=c[:,0]/np.maximum(c[:,1],1e-12)
    assert np.all(np.diff(loss,axis=2)<=1e-6) and np.all(loss[:,:,-1]==0)
    assert np.all(work[:,-1]==len(base)) and np.all(np.diff(work,axis=1)>=0)
    return loss,work,feature,dict(build_seconds=build,trace_seconds=time.perf_counter()-t,zero_distance_queries=zero,centroid_distances=nlist)
def crc(loss):
    valid=np.flatnonzero((loss.sum(0)+1)/(len(loss)+1)<=ALPHA)
    return int(valid[0]) if len(valid) else loss.shape[1]-1
def gather(loss,s,p):return loss[np.arange(len(loss)),s,p[s]]
def ci(v):
    rng=np.random.default_rng(42)
    return np.quantile([v[rng.integers(len(v),size=len(v))].mean() for _ in range(1000)],[.025,.975]).tolist()
def evaluate(name,seed,loss,work,feature):
    design=slice(0,400);cal=slice(400,1400);pilot=slice(1400,2000)
    template=np.array([crc(loss[design,j])+1 for j in range(3)])
    family=np.unique(np.clip(np.ceil(np.r_[0,np.geomspace(1/64,64,128)][:,None]*template),1,P).astype(int),axis=0)-1
    naive=np.array([crc(loss[cal,j]) for j in range(3)])
    worst=np.stack([np.max(np.stack([loss[cal,j,p[j]] for j in range(3)],axis=1),axis=1) for p in family],axis=1)
    envelope=family[crc(worst)]
    # Bounding each marginal k-risk simultaneously is insufficient for
    # query-dependent k. Bound the per-query max loss, uniformly over budgets.
    penalty=np.sqrt(np.log(len(family)/.05)/2000)
    valid=np.flatnonzero(worst.mean(axis=0)+penalty<=ALPHA)
    union=family[valid[0]] if len(valid) else np.full(3,P-1)
    selectors={f'ambiguity_q{x}':np.where(feature>np.quantile(feature[design],x),2,0) for x in [.25,.5,.75]}
    selectors['inverse_q0.5']=2-selectors['ambiguity_q0.5']
    selectors['uniform']=np.random.default_rng(888).integers(0,3,len(loss))
    for j,k in enumerate(KS):selectors[f'constant_{k}']=np.full(len(loss),j)
    rows=[];arrays={}
    for selector,s in selectors.items():
        common=np.repeat(crc(loss[cal][np.arange(1000),s[cal],:]),3)
        mixed=np.stack([gather(loss[cal],s[cal],p) for p in family],axis=1)
        policies=dict(naive_per_k=naive,selector_common_crc=common,selector_scaled_crc=family[crc(mixed)],
            envelope_crc=envelope,simultaneous_hoeffding=union,exact=np.full(3,P-1))
        for method,p in policies.items():
            v=gather(loss[pilot],s[pilot],p);w=work[pilot][np.arange(600),p[s[pilot]]];interval=ci(v)
            key=selector+'__'+method;arrays[key+'__loss']=v;arrays[key+'__work']=w
            rows.append(dict(dataset=name,seed=seed,selector=selector,method=method,fnr=float(v.mean()),
                ci_low=interval[0],ci_high=interval[1],distances=float(w.mean()),probes=float((p[s[pilot]]+1).mean()),
                budgets=(p+1).tolist(),k_histogram=np.bincount(s[pilot],minlength=3).tolist()))
    return rows,arrays
def smoke():
    rng=np.random.default_rng(0);base=rng.normal(size=(90,4)).astype('f');q=rng.normal(size=(11,4)).astype('f')
    loss,work,_,_=trace(base,q,0,8)
    model=MiniBatchKMeans(n_clusters=8,random_state=0,n_init=3,batch_size=1024,max_iter=100)
    labels=model.fit_predict(base);order=np.argsort(dist(q,model.cluster_centers_),axis=1,kind='stable');d=dist(q,base)
    for i in range(len(q)):
        truth=np.argsort(d[i],kind='stable')
        for p in range(1,9):
            c=np.flatnonzero(np.isin(labels,order[i,:p]));ann=c[np.argsort(d[i,c],kind='stable')]
            assert work[i,p-1]==len(c)
            for j,k in enumerate(KS):assert abs(1-len(set(truth[:k])&set(ann[:k]))/k-loss[i,j,p-1])<1e-6
    assert crc(np.ones((10,3)))==2 and crc(np.c_[np.ones(100),np.zeros(100)])==1
    save(ROOT/'smoke.json',dict(passed=True,checks=['brute-force candidate recall for all k/probes','nested losses and costs',
        'full-search exactness','CRC correction and fallback'],python=platform.python_version()))
    print('Smoke passed',flush=True)
def aggregate():
    rows=[]
    for path in sorted((ROOT/'results').glob('*_metrics.json')):rows+=json.loads(path.read_text())['rows']
    with open(ROOT/'results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    primary=[r for r in rows if r['selector']=='ambiguity_q0.5' and r['method']=='naive_per_k']
    counts={d:sum(r['fnr']>.13 and r['ci_low']>.1 for r in primary if r['dataset']==d) for d in ['glove','fashion']}
    complete=all(sum(r['dataset']==d for r in primary)==5 for d in counts)
    gate=dict(failure_counts=counts,complete_five_seed_two_dataset_pilot=complete,opportunity_gate_passed=complete and all(v>=4 for v in counts.values()),novelty_established=False,reserved_queries_evaluated=False)
    save(ROOT/'gate.json',gate);print(json.dumps(gate),flush=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,3.5),sharey=True)
    for ax,d in zip(axes,counts):
        for method in ['naive_per_k','selector_common_crc','selector_scaled_crc','envelope_crc','simultaneous_hoeffding']:
            rr=[r for r in rows if r['dataset']==d and r['selector']=='ambiguity_q0.5' and r['method']==method]
            if rr:ax.scatter(np.mean([r['distances'] for r in rr]),np.mean([r['fnr'] for r in rr]),label=method)
        ax.axhline(.1,color='black',linestyle='--');ax.set_title(d);ax.set_xlabel('Mean corpus-vector distances')
    axes[0].set_ylabel('Mean FNR across index seeds');axes[1].legend(fontsize=7)
    fig.tight_layout();fig.savefig(ROOT/'pilot.png',dpi=180);fig.savefig(ROOT/'pilot.pdf');plt.close(fig)
def run(args):
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for name in args.datasets:
        base,q,provenance=load(args.data,name);save(out/(name+'_provenance.json'),provenance)
        for seed in args.seeds:
            t=time.perf_counter();loss,work,feat,timing=trace(base,q,seed);rows,arrays=evaluate(name,seed,loss,work,feat)
            np.savez_compressed(out/f'{name}_{seed}_pilot.npz',**arrays)
            save(out/f'{name}_{seed}_metrics.json',dict(rows=rows,timing=timing,total_seconds=time.perf_counter()-t))
            print(name,seed,'naive primary FNR',next(r['fnr'] for r in rows if r['selector']=='ambiguity_q0.5' and r['method']=='naive_per_k'),flush=True)
    aggregate()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['smoke','pilot','aggregate']);p.add_argument('--data',type=Path,default=ROOT.parents[1]/'work'/'datasets')
    p.add_argument('--datasets',nargs='+',default=['glove','fashion']);p.add_argument('--seeds',nargs='+',type=int,default=list(range(5)));args=p.parse_args()
    with threadpool_limits(limits=1):
        if args.action=='smoke':smoke()
        elif args.action=='pilot':run(args)
        else:aggregate()
