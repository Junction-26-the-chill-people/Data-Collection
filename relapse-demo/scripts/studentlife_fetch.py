"""Fetch only GPS/PAM/sleep/PHQ ZIP members from the CC-BY4 Zenodo derivative.
No R runtime, archive extraction or object execution. Partial archive integrity is explicit.
"""
import urllib.request,json,struct,zlib,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent/'datasets/location_sources/studentlife_zenodo'

def main():
    j=json.loads((BASE/'record.json').read_text());f=j['files'][0];url=f['links']['self'];size=f['size'];headers=[]
    def get(start,length):
        assert 0<length<4000000
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={start}-{start+length-1}','User-Agent':'Junction26-research/1.0'}),timeout=30) as r:
                    assert r.status==206 and r.headers['Content-Range'].startswith(f'bytes {start}-')
                    headers.append({'range':r.headers['Content-Range'],'etag':r.headers.get('ETag'),'lastModified':r.headers.get('Last-Modified')})
                    b=r.read(length+1);assert len(b)==length;return b
            except Exception:
                if attempt==2:raise
    tail=get(size-65557,65557);pos=tail.rfind(b'PK\x05\x06');v=struct.unpack_from('<4s4H2LH',tail,pos);cdsize,cdoffset=v[5:7];central=tail[cdoffset-(size-len(tail)):];at=0;manifest=[];raw=BASE/'raw';raw.mkdir(exist_ok=True)
    wanted={'dataset_rds/sensing/gps.Rds','dataset_rds/EMA/PAM.Rds','dataset_rds/EMA/Sleep.Rds','dataset_rds/survey/PHQ-9.Rds'}
    while central[at:at+4]==b'PK\x01\x02':
        v=struct.unpack_from('<4s6H3L5H2L',central,at);n,e,c=v[10:13];name=central[at+46:at+46+n].decode();at+=46+n+e+c
        if name not in wanted:continue
        filename=Path(name).name;dest=raw/filename
        if dest.exists():data=dest.read_bytes()
        else:
            chunk=get(v[16],v[8]+4096);h=struct.unpack_from('<4s5H3L2H',chunk);assert h[0]==b'PK\x03\x04';start=30+h[9]+h[10];packed=chunk[start:start+v[8]];assert v[4] in [0,8]
            if v[4]==8:
                decoder=zlib.decompressobj(-15);data=decoder.decompress(packed,v[9]+1);assert decoder.eof and not decoder.unused_data
            else:data=packed
            assert len(data)==v[9] and zlib.crc32(data)&0xffffffff==v[7];dest.write_bytes(data)
        assert len(data)==v[9] and zlib.crc32(data)&0xffffffff==v[7]
        manifest.append({'file':filename,'archiveMember':name,'bytes':len(data),'compressedBytes':v[8],'zipCRC32':hex(v[7]),'sha256':hashlib.sha256(data).hexdigest(),'archiveURL':url});print(filename,len(data),flush=True)
    (BASE/'member-manifest.json').write_text(json.dumps({'sourceDOI':'10.5281/zenodo.3529253','sourceVersion':'1.0.0','license':'CC-BY-4.0','archiveBytes':size,'publisherArchiveMD5':'353ae79f157097a57bff1c004634ba1b','fullArchiveMD5Verified':False,'method':'Selected ZIP members fetched via HTTP Range, deflate decompressed and ZIPCRC verified; RDS bytes preserved. No whole archive downloaded.','responseHeaders':headers,'files':manifest},indent=2),encoding='utf-8')
if __name__=='__main__':main()
