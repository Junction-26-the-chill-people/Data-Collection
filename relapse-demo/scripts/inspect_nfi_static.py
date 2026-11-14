"""Non-executing pickle opcode inspector. GLOBAL/REDUCE/BUILD remain inert dictionaries.
Never imports named globals, calls constructors, or uses pickle.load/Unpickler.
"""
from pathlib import Path
import pickletools,json
MARK=object()
def inspect_pickle(path):
 stack=[];memo={}
 def marked():
  i=next(i for i in range(len(stack)-1,-1,-1) if stack[i] is MARK)
  items=stack[i+1:];del stack[i:];return items
 for op,arg,pos in pickletools.genops(path.read_bytes()):
  n=op.name
  if n in ('PROTO','FRAME'):continue
  if n=='MARK':stack.append(MARK)
  elif n in ('SHORT_BINUNICODE','BINUNICODE','UNICODE','BININT','BININT1','BININT2','BINFLOAT','BINBYTES','SHORT_BINBYTES'):stack.append(arg)
  elif n=='NONE':stack.append(None)
  elif n=='NEWTRUE':stack.append(True)
  elif n=='NEWFALSE':stack.append(False)
  elif n=='EMPTY_DICT':stack.append({})
  elif n=='EMPTY_LIST':stack.append([])
  elif n=='EMPTY_TUPLE':stack.append(())
  elif n=='MEMOIZE':memo[len(memo)]=stack[-1]
  elif n in ('BINGET','LONG_BINGET'):stack.append(memo[arg])
  elif n=='STACK_GLOBAL':
   name=stack.pop();module=stack.pop();stack.append({'global':module+'.'+name})
  elif n in ('REDUCE','NEWOBJ'):
   args=stack.pop();func=stack.pop();stack.append({'operation':n,'callable':func,'args':args})
  elif n=='BUILD':
   state=stack.pop();stack[-1]['state']=state
  elif n=='TUPLE':stack.append(tuple(marked()))
  elif n in ('TUPLE1','TUPLE2','TUPLE3'):
   size=int(n[-1]);items=stack[-size:];del stack[-size:];stack.append(tuple(items))
  elif n=='APPENDS':items=marked();stack[-1].extend(items)
  elif n=='SETITEM':v=stack.pop();k=stack.pop();stack[-1][k]=v
  elif n=='SETITEMS':
   items=marked();stack[-1].update(zip(items[::2],items[1::2]))
  elif n=='STOP':return stack[-1]
  else:raise ValueError('Unsupported opcode '+n)
 raise ValueError('No STOP')
def shape(x,depth=0):
 if depth>9:return type(x).__name__
 if isinstance(x,bytes):return {'bytes':len(x)}
 if isinstance(x,dict):return {str(k):shape(v,depth+1) for k,v in x.items()}
 if isinstance(x,(tuple,list)):
  if len(x)>8:return {'length':len(x),'first':[shape(v,depth+1) for v in x[:4]]}
  return [shape(v,depth+1) for v in x]
 return x
if __name__=='__main__':
 p=Path(__file__).resolve().parents[2]/'datasets/nfi_fared_digital_traces/raw/df_dict_healthdb_steps.pkl'
 print(json.dumps(shape(inspect_pickle(p)),indent=2)[:14000])
