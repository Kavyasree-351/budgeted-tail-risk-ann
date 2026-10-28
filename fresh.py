"""Fresh calibration from unused TRAIN rows; no reserved TEST queries."""
import gzip
import h5py
import numpy as np
from data import hdf5_rows,image_rows
def unused_ids(count,corpus_ids,seed,n):
    forbidden=set(corpus_ids);seen=set();out=[];rng=np.random.default_rng(88000+seed)
    while len(out)<n:
        for value in rng.integers(count,size=n):
            value=int(value)
            if value not in forbidden and value not in seen:out.append(value);seen.add(value)
            if len(out)==n:break
    return np.array(out)
def calibration_queries(name,seed,data,corpus_ids,n=5000):
    if name=='glove':
        with h5py.File(data/'glove-25-angular.hdf5') as f:
            ids=unused_ids(len(f['train']),corpus_ids,seed,n)
            q=hdf5_rows(f['train'],ids)
        q/=np.maximum(np.linalg.norm(q,axis=1,keepdims=True),1e-12)
    else:
        ids=unused_ids(60000,corpus_ids,seed,n)
        q=image_rows(data/'train-images-idx3-ubyte.gz',ids)
    assert len(set(ids))==n and not(set(ids)&set(corpus_ids))
    return q,ids
