from PIL import Image
import numpy as np, json, sys
from collections import deque
from scipy import ndimage
def cut(path):
  im=np.array(Image.open(path).convert('RGB')).astype(int); H,W,_=im.shape
  border=np.concatenate([im[0],im[-1],im[:,0],im[:,-1]]); bg=np.median(border,0)
  dist=np.abs(im-bg).max(2); bri=im.mean(2); neutral=(im.max(2)-im.min(2))<12
  dark=(dist>40)&~((neutral)&(bri>110))   # "echte" Figurpixel für Bodenlinie
  mask=np.zeros((H,W),bool); q=deque([(y,x) for x in range(W) for y in (0,H-1)]+[(y,x) for y in range(H) for x in (0,W-1)])
  # Bodenlinie je Spalte grob: unterste dunkle Zeile in der Nähe
  rows_dark=dark.any(1)
  while q:
    y,x=q.popleft()
    if y<0 or x<0 or y>=H or x>=W or mask[y,x]: continue
    if not (dist[y,x]<16 or (neutral[y,x] and bri[y,x]>118 and dist[y,x]<95 and ground_band[y,x])): continue
    mask[y,x]=True; q.extend(((y+1,x),(y-1,x),(y,x+1),(y,x-1)))
  return im,mask,bg
def ground_bands(path):
  im=np.array(Image.open(path).convert('RGB')).astype(int)
  return im
results={}
for name in sys.argv[1:]:
  im=np.array(Image.open(name).convert('RGB')).astype(int); H,W,_=im.shape
  border=np.concatenate([im[0],im[-1],im[:,0],im[:,-1]]); bg=np.median(border,0)
  dist=np.abs(im-bg).max(2); bri=im.mean(2); neutral=(im.max(2)-im.min(2))<12
  fig=(dist>45)&~(neutral&(bri>115))
  lab,n=ndimage.label(ndimage.binary_dilation(fig,iterations=6))
  objs=ndimage.find_objects(lab)
  comps=[]
  for i,sl in enumerate(objs):
    area=(lab[sl]==i+1).sum()
    if area<3000: continue
    comps.append((sl[0].start,sl[0].stop,sl[1].start,sl[1].stop,area))
  comps.sort(key=lambda c:(round(c[1]/120),c[2]))
  results[name]=[list(map(int,c[:4])) for c in comps]
  print(name,bg,len(comps)); [print('  ',c) for c in comps]
json.dump(results,open('comps.json','w'))
