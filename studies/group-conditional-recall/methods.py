"""Established groupwise CRC and bounded-KL controls; not new algorithms."""
import numpy as np
P=64;ALPHA=.1
def crc(loss):
    if len(loss)==0:return loss.shape[1]-1
    ok=np.flatnonzero((loss.sum(axis=0)+1)/(len(loss)+1)<=ALPHA)
    return int(ok[0]) if len(ok) else loss.shape[1]-1
def kl_crc(loss,groups=10,delta=.05):
    if len(loss)==0:return loss.shape[1]-1
    z=loss.mean(axis=0);a=ALPHA
    # KL(0||a) is finite; use continuous endpoint convention.
    zz=np.clip(z,1e-15,1-1e-15)
    divergence=zz*np.log(zz/a)+(1-zz)*np.log((1-zz)/(1-a))
    ok=np.flatnonzero((z<=a)&(len(loss)*divergence>=np.log(groups*loss.shape[1]/delta)))
    return int(ok[0]) if len(ok) else loss.shape[1]-1
def feature(coarse):
    two=np.partition(coarse,1,axis=1)[:,:2];two.sort(axis=1)
    return np.where(two[:,1]<=1e-15,1.,np.sqrt(two[:,0]/np.maximum(two[:,1],1e-15)))
def bins(f,edges):return np.searchsorted(edges,f,side='right')
def calibrate(loss,g,held,random_group):
    p=crc(loss);per=np.array([crc(loss[g==j]) for j in range(10)])
    five=np.array([crc(loss[g//2==j]) for j in range(5)])
    two=np.array([crc(loss[(g>=8)==bool(j)]) for j in range(2)])
    return dict(global_crc=np.repeat(p,10),group_crc10=per,monotone_crc10=np.maximum.accumulate(per),
        worst_uniform=np.repeat(per.max(),10),group_crc5=np.repeat(five,2),group_crc2=np.r_[np.repeat(two[0],8),np.repeat(two[1],2)],
        shuffled_crc10=np.array([crc(loss[random_group==j]) for j in range(10)]),
        group_kl10=np.array([kl_crc(loss[g==j]) for j in range(10)]),
        ood_exact_fallback=np.repeat(p,10),exact=np.repeat(loss.shape[1]-1,10))
def budgets(method,policy,g,held,random_group,ood_scenario):
    p=policy[random_group] if method=='shuffled_crc10' else policy[g]
    if method=='ood_exact_fallback' and ood_scenario:p=np.where(held,P-1,p)
    return p
