"""Public inputs and permanently separated exploratory/reserved query IDs."""
import gzip,hashlib,json
from pathlib import Path
import h5py
import numpy as np
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'work'/'datasets'
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return h.hexdigest()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2),encoding='utf-8')
def hdf5_rows(dataset,ids,block=8192):
    ids=np.asarray(ids);order=np.argsort(ids);sorted_ids=ids[order]
    out=np.empty((len(ids),dataset.shape[1]),dtype='f')
    for lo in range(0,len(dataset),block):
        hi=min(lo+block,len(dataset));a,b=np.searchsorted(sorted_ids,[lo,hi])
        if b>a:out[order[a:b]]=np.asarray(dataset[lo:hi],dtype='f')[sorted_ids[a:b]-lo]
    return out
def image_rows(path,ids,block=1024):
    ids=np.asarray(ids);order=np.argsort(ids);sorted_ids=ids[order]
    with gzip.open(path,'rb') as f:
        head=np.frombuffer(f.read(16),dtype='>u4');assert head[0]==2051
        count=int(head[1]);dim=int(head[2]*head[3]);out=np.empty((len(ids),dim),dtype='f')
        for lo in range(0,count,block):
            hi=min(lo+block,count);raw=np.frombuffer(f.read((hi-lo)*dim),dtype='u1').reshape(hi-lo,dim)
            a,b=np.searchsorted(sorted_ids,[lo,hi])
            if b>a:out[order[a:b]]=raw[sorted_ids[a:b]-lo]
    return out
def load(name,seed,data=DATA):
    previous=json.loads((ROOT/'inputs'/f'{name}.json').read_text())
    for file,expected in previous['files'].items():
        assert digest(data/file)==expected,'Public data bytes changed: '+file
    pool=np.array(previous['design_ids']+previous['calibration_ids']+previous['pilot_ids'])
    rng=np.random.default_rng(17000+seed);used=rng.permutation(pool)
    if name=='glove':
        with h5py.File(data/'glove-25-angular.hdf5') as f:
            bi=np.sort(rng.choice(len(f['train']),20000,replace=False))
            # Reading the public corpus contiguously avoids h5py's expensive
            # large fancy-index selection; reserved QUERY vectors stay unread.
            base=hdf5_rows(f['train'],bi);o=np.argsort(used)
            query=np.asarray(f['test'][used[o]],dtype='f')[np.argsort(o)]
        base/=np.maximum(np.linalg.norm(base,axis=1,keepdims=True),1e-12)
        query/=np.maximum(np.linalg.norm(query,axis=1,keepdims=True),1e-12)
    else:
        bi=np.sort(rng.choice(60000,10000,replace=False))
        # Integer-valued float32 pixels give exact float64 squared distances;
        # uniform scaling is immaterial to Euclidean neighbor order.
        base=image_rows(data/'train-images-idx3-ubyte.gz',bi)
        query=image_rows(data/'t10k-images-idx3-ubyte.gz',used)
    reserved=set(previous['reserved_unevaluated_ids']);assert not(set(used)&reserved)
    assert len(set(used))==2000
    provenance=dict(dataset=name,seed=seed,files=previous['files'],base_size=len(base),dimension=base.shape[1],
        corpus_ids=bi.tolist(),design_ids=used[:400].tolist(),calibration_ids=used[400:1400].tolist(),
        pilot_ids=used[1400:].tolist(),reserved_unevaluated_ids=sorted(reserved))
    return base,query[:400],query[400:1400],query[1400:],provenance
