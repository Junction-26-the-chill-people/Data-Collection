from pathlib import Path
import sys,pickle,tempfile,unittest,struct
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from inspect_nfi_static import inspect_pickle
from summarize_nfi_static import array
class InertParserTests(unittest.TestCase):
 def inspect(self,obj):
  with tempfile.TemporaryDirectory(dir=ROOT/'.tmp') as d:
   p=Path(d)/'fixture.pkl';p.write_bytes(pickle.dumps(obj,protocol=4));return inspect_pickle(p)
 def test_primitives(self):
  obj={'items':[1,2,3],'tuple':(4,5),'raw':b'abc','missing':None}
  self.assertEqual(self.inspect(obj),obj)
 def test_reducer_not_executed(self):
  class Payload:
   def __reduce__(self):return (eval,('1/0',))
  tree=self.inspect(Payload());self.assertEqual(tree['operation'],'REDUCE');self.assertEqual(tree['callable']['global'],'builtins.eval');self.assertEqual(tree['args'],('1/0',))
 def test_unsupported_opcode_rejected(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.tmp') as d:
   p=Path(d)/'fixture.pkl';p.write_bytes(b'Pexternal-reference\n.')
   with self.assertRaisesRegex(ValueError,'Unsupported opcode'):inspect_pickle(p)
class BufferTests(unittest.TestCase):
 def node(self,endian='<',shape=(1,2),fortran=False):
  return {'callable':{'global':'numpy._core.multiarray._reconstruct'},'state':(1,shape,{'args':('f8',),'state':(3,endian)},fortran,struct.pack(endian+'dd',1.25,-2.5))}
 def test_little_and_big_endian(self):
  for endian in ('<','>'):self.assertEqual(array(self.node(endian))[0],[1.25,-2.5])
 def test_shape_mismatch(self):
  with self.assertRaisesRegex(ValueError,'shape mismatch'):array(self.node(shape=(1,3)))
 def test_fortran_rejected(self):
  with self.assertRaisesRegex(ValueError,'Fortran'):array(self.node(fortran=True))

if __name__=='__main__':unittest.main()
