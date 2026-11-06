from PIL import Image, ImageFilter
import numpy as np
from collections import deque
im=np.array(Image.open('src.jpg').convert('RGB')).astype(int)
H,W,_=im.shape
bg=np.array([213,213,213])
dist=np.abs(im-bg).max(2)
bri=im.mean(2); neutral=(im.max(2)-im.min(2))<10
# Flood vom Rand: Hintergrund
mask=np.zeros((H,W),bool); q=deque()
for x in range(W):
  for y in (0,H-1): q.append((y,x))
for y in range(H):
  for x in (0,W-1): q.append((y,x))
def ok(y,x):
  if dist[y,x]<16: return True
  # Schatten / Bodenwirbel: neutral grau, nur im Bodenbereich
  if y>=548 and neutral[y,x] and bri[y,x]>115: return True
  return False
while q:
  y,x=q.popleft()
  if y<0 or x<0 or y>=H or x>=W or mask[y,x] or not ok(y,x): continue
  mask[y,x]=True; q.extend(((y+1,x),(y-1,x),(y,x+1),(y,x-1)))
alpha=~mask
# Kanten-Halos (helle JPEG-Ränder) abtragen
for it in range(2):
  a=alpha.copy()
  edge=a & (~np.roll(a,1,0)|~np.roll(a,-1,0)|~np.roll(a,1,1)|~np.roll(a,-1,1))
  alpha[edge & (bri>170) & neutral]=False
rgba=np.dstack([im.clip(0,255),alpha*255]).astype(np.uint8)
full=Image.fromarray(rgba,'RGBA'); full.save('cut_full.png')
segs=[(36,352),(375,771),(799,1256)]
FEET=None
outs=[]
for i,(x0,x1) in enumerate(segs):
  sub=alpha[:,x0:x1]; ys=np.where(sub.any(1))[0]; xs=np.where(sub.any(0))[0]
  print(i,'bbox',x0+xs.min(),x0+xs.max(),ys.min(),ys.max())
  outs.append((x0+xs.min()-4,ys.min()-4,x0+xs.max()+5,ys.max()+5))
np.save('alpha.npy',alpha)
print(outs)
