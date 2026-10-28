"""Download only public data; verify the exact pilot bytes from provenance."""
import argparse,urllib.request
import research as r
p=argparse.ArgumentParser();p.add_argument('--data',type=r.Path,default=r.ROOT.parents[1]/'work'/'datasets');a=p.parse_args()
a.data.mkdir(parents=True,exist_ok=True)
sources={'glove-25-angular.hdf5':'https://huggingface.co/datasets/hhy3/ann-datasets/resolve/0bc1ed6/glove-25-angular.hdf5',
         'train-images-idx3-ubyte.gz':'https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/train-images-idx3-ubyte.gz',
         't10k-images-idx3-ubyte.gz':'https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/t10k-images-idx3-ubyte.gz'}
expected={}
for file in (r.ROOT/'results').glob('*_provenance.json'):expected.update(r.json.loads(file.read_text())['files'])
for name,url in sources.items():
    target=a.data/name
    if not target.exists():
        temp=target.with_suffix(target.suffix+'.part')
        urllib.request.urlretrieve(url,temp);temp.replace(target)
    digest=r.sha(target)
    if name in expected and digest!=expected[name]:raise RuntimeError('Checksum mismatch: '+name)
    print(name,digest)
