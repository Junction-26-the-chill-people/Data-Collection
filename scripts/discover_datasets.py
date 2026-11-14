import urllib.request,json,concurrent.futures
urls={
'hf_info':'https://huggingface.co/api/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces',
'hf_tree':'https://huggingface.co/api/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces/tree/main?recursive=true&expand=false&limit=1000',
'zenodo':'https://zenodo.org/api/records/5085146',
'dryad':'https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.qz612jmrn'
}
def fetch(item):
 k,u=item
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Junction26-research-download/1.0'}),timeout=45) as r: data=r.read()
  open('datasets/'+k+'_metadata.json','wb').write(data)
  obj=json.loads(data)
  if k=='hf_tree': out=obj
  elif k=='hf_info': out={x:obj.get(x) for x in ['id','sha','gated','private','cardData','siblings']}
  elif k=='zenodo': out={x:obj.get(x) for x in ['id','files','metadata']}
  else: out=obj
  print(k,json.dumps(out)[:18000],flush=True)
 except Exception as e: print(k,type(e).__name__,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(fetch,urls.items()))
