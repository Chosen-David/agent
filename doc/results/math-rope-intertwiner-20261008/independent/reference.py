from decimal import Decimal as D, getcontext
from fractions import Fraction as F
getcontext().prec=75
class Z:
 def __init__(self,x=0,y=0):self.x=D(x);self.y=D(y)
 def __add__(self,z):return Z(self.x+z.x,self.y+z.y)
 def __sub__(self,z):return Z(self.x-z.x,self.y-z.y)
 def __mul__(self,z):return Z(self.x*z.x-self.y*z.y,self.x*z.y+self.y*z.x)
 def conj(self):return Z(self.x,-self.y)
 def sq(self):return self.x*self.x+self.y*self.y
 def __abs__(self):return self.sq().sqrt()
def trig(t):
 # Taylor convergence at the finite fixture horizons (|t| <= 90).
 ss=D(0);cc=D(0);s=t;c=D(1)
 for k in range(400):
  ss+=s;cc+=c
  s*= -t*t/D((2*k+2)*(2*k+3));c*= -t*t/D((2*k+1)*(2*k+2))
 return Z(cc,ss)
def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def sub(A,B):return [[a-b for a,b in zip(r,s)] for r,s in zip(A,B)]
def rank(A):
 A=[list(map(F,row)) for row in A];pivot=0
 for col in range(len(A[0])):
  rows=[i for i in range(pivot,len(A)) if A[i][col]]
  if not rows:continue
  i=rows[0];A[pivot],A[i]=A[i],A[pivot];d=A[pivot][col];A[pivot]=[v/d for v in A[pivot]]
  for j in range(len(A)):
   if j!=pivot:
    d=A[j][col];A[j]=[a-d*b for a,b in zip(A[j],A[pivot])]
  pivot+=1
  if pivot==len(A):break
 return pivot
def transpose(A):return list(map(list,zip(*A)))
def dim(A,B):
 n=len(A);m=len(B);cols=[]
 for i in range(m):
  for j in range(n):
   T=[[F(int(k==i and l==j)) for l in range(n)] for k in range(m)]
   cols.append(sum(sub(mm(T,A),mm(B,T)),[]))
 return n*m-rank(transpose(cols))
def diag(*blocks):
 size=sum(map(len,blocks));out=[[F(0)]*size for _ in range(size)];i=0
 for block in blocks:
  for j,row in enumerate(block):out[i+j][i:i+len(row)]=row
  i+=len(block)
 return out
