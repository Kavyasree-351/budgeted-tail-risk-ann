"""Budget-feasibility primitives and known multi-risk fixed-sequence tests."""
import numpy as np
TARGET=np.array([.10,.10,.05]);DELTA_PLUS=.025;DELTA_MINUS=.025
GROUP_NAMES=['all']+[f'ambiguity_D{i}' for i in range(1,11)]+['near','far','upper_ambiguity_near','upper_ambiguity_far']
RISK_NAMES=['mean_FNR','Pr_FNR_gt_0.20','Pr_FNR_gt_0.50']
def add_zero(loss,work):return np.c_[np.ones(len(loss)),loss],np.c_[np.zeros(len(work),dtype=int),work]+64
def features(coarse):
    two=np.partition(coarse,1,axis=1)[:,:2];two.sort(axis=1)
    return np.sqrt(two[:,0]/np.maximum(two[:,1],1e-15)),np.sqrt(two[:,0])
def groups_and_cells(coarse,edges,median):
    a,d=features(coarse);g=np.searchsorted(edges,a,side='right');far=d>=median
    groups=np.column_stack([np.ones(len(g),dtype=bool)]+[g==j for j in range(10)]+[~far,far,(g>=5)&~far,(g>=5)&far])
    return groups,(g//2)*2+far.astype(int),g
def components(loss):return np.stack([loss,(loss>.20+1e-12).astype(float),(loss>.50+1e-12).astype(float)],axis=-1)
def risks(loss,groups):
    n=groups.sum(0);return groups.T@components(loss)/np.maximum(n[:,None],1),n
def bernoulli_kl(z,a):
    z=np.clip(z,1e-15,1-1e-15)
    return z*np.log(z/a)+(1-z)*np.log((1-z)/(1-a))
def test_values(loss,groups,lower=False):
    z,n=risks(loss,groups);valid=(z>TARGET) if lower else (z<TARGET)
    p=np.where(valid,np.exp(-n[:,None]*bernoulli_kl(z,TARGET)),1.)
    p[n==0]=1.
    return p,z,n
def max_prefix(work,cap):
    assert np.all(np.diff(work,axis=1)>=0)
    return (work<=cap).sum(axis=1)-1
def apply(policy,cells,pmax):return np.minimum(np.asarray(policy)[cells],pmax)
def evaluate(loss,work,policy,cells,pmax):
    p=apply(policy,cells,pmax);q=np.arange(len(loss));return loss[q,p],work[q,p],p
def infeasibility(loss,work,groups,cap):
    p=max_prefix(work,cap);v=loss[np.arange(len(loss)),p];pv,z,n=test_values(v,groups,True)
    j=np.unravel_index(np.argmin(pv),pv.shape);reject=bool(pv[j]<=DELTA_MINUS/pv.size)
    return dict(rejected=reject,group=GROUP_NAMES[j[0]],risk=RISK_NAMES[j[1]],pvalue=float(pv[j]),
        threshold=DELTA_MINUS/pv.size,calibration_risk=float(z[j]),target=float(TARGET[j[1]]),n=int(n[j[0]]))
def select(path,loss,work,groups,cells,cap):
    """LTT: a path fixed by DESIGN, checked safest -> cheapest, stop on failure."""
    pmax=max_prefix(work,cap);witness=infeasibility(loss,work,groups,cap)
    if witness['rejected']:return None,dict(status='nominal_infeasible',tests=0,witness=witness)
    last=None;tests=0;last_p=None
    for policy in reversed(path):
        # Only unconditional full search permits deterministic zero-risk bypass.
        exact=bool(cap>=work[0,-1] and np.all(np.asarray(policy)==64))
        v,_,_=evaluate(loss,work,policy,cells,pmax)
        p=0. if exact else float(test_values(v,groups)[0].max());tests+=1
        if p>DELTA_PLUS:break
        last=policy.copy();last_p=p
    return last,dict(status='nominal_certified' if last is not None else 'uncertified',tests=tests,
        last_joint_pvalue=last_p,witness=witness)
def crc(loss):
    if len(loss)==0:return 64
    ok=np.flatnonzero((loss.sum(0)+1)/(len(loss)+1)<=.1)
    return int(ok[0]) if len(ok) else 64
def deduplicate(path):
    out=[]
    for p in path:
        if not out or not np.array_equal(out[-1],p):out.append(np.asarray(p,dtype=int).copy())
    return np.stack(out)
def uniform_path():return np.repeat(np.arange(65)[:,None],10,axis=1)
def template_path(loss,cells):
    p=np.array([crc(loss[cells==c]) for c in range(10)])
    return deduplicate([np.clip(p+offset,0,64) for offset in range(-64,65)])
def repair_path(loss,work,groups,cells,cap,variant='full'):
    """Design-only greedy risk reduction per added distance; no optimality claim."""
    n=len(loss);pmax=max_prefix(work,cap);eff=np.minimum(np.arange(65)[None,:],pmax[:,None])
    clipped_loss=loss[np.arange(n)[:,None],eff];clipped_work=work[np.arange(n)[:,None],eff]
    v=components(clipped_loss);ng=groups.sum(0);contrib=np.zeros((10,65,groups.shape[1]*3));cost=np.zeros((10,65))
    for c in range(10):
        take=cells==c
        if not take.any():continue
        z=np.einsum('qps,qg->pgs',v[take],groups[take].astype(float))/np.maximum(ng[None,:,None],1)
        contrib[c]=z.reshape(65,-1);cost[c]=clipped_work[take].sum(0)/n
    weights=np.broadcast_to(1/TARGET,(groups.shape[1],3)).copy()
    if variant=='no_overlap':weights[11:]=0
    if variant=='no_tail':weights[:,1:]=0
    weights=weights.ravel();current=np.zeros(10,dtype=int);path=[current.copy()]
    for _ in range(640):
        best=None;best_score=0.
        for c in range(10):
            gain=(contrib[c,current[c]]-contrib[c])@weights;extra=cost[c]-cost[c,current[c]]
            allowed=(np.arange(65)>current[c])&(extra>1e-12)&(gain>1e-12)
            score=np.full(65,-np.inf);np.divide(gain,extra,out=score,where=allowed)
            p=int(np.argmax(score))
            if score[p]>best_score:best_score=float(score[p]);best=(c,p)
        if best is None:break
        current[best[0]]=best[1];path.append(current.copy())
    while np.any(current<64):current=np.minimum(current+1,64);path.append(current.copy())
    result=deduplicate(path);assert np.all(np.diff(result,axis=0)>=0)
    return result
def empirical_cvar(v,tau=.9):
    if len(v)==0:return None
    order=np.sort(v)[::-1];mass=(1-tau)*len(v);whole=int(np.floor(mass));fraction=mass-whole
    return float((order[:whole].sum()+(fraction*order[whole] if whole<len(v) else 0))/mass)
