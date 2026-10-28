"""Design-only numeric audit; does not inspect new held-out data."""
import argparse
import numpy as np
import research as r
from threadpoolctl import threadpool_limits
p=argparse.ArgumentParser();p.add_argument('--data',type=r.Path,default=r.ROOT.parents[1]/'work'/'datasets');args=p.parse_args()
report={}
with threadpool_limits(limits=1):
    for name in ['glove','fashion']:
        b,q,_=r.load(args.data,name)
        a=r.dist(q[:20],b);d=r.dist(q[:20].astype(float),b.astype(float))
        i=np.argsort(a,axis=1,kind='stable')[:,:50];j=np.argsort(d,axis=1,kind='stable')[:,:50]
        report[name]=dict(top50_set_disagreements=sum(set(x)!=set(y) for x,y in zip(i,j)),queries_checked=20)
r.save(r.ROOT/'precision_audit.json',report);print(report)
