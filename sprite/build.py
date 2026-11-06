from PIL import Image
import numpy as np, json, base64, io
from scipy import ndimage
def frames_from(path, names, scale, centroid_modes):
  im=np.array(Image.open(path).convert('RGB')).astype(int); H,W,_=im.shape
  border=np.concatenate([im[0],im[-1],im[:,0],im[:,-1]]); bg=np.median(border,0)
  dist=np.abs(im-bg).max(2); bri=im.mean(2); neutral=(im.max(2)-im.min(2))<12
  fig=(dist>45)&~(neutral&(bri>115))
  lab,n=ndimage.label(ndimage.binary_dilation(fig,iterations=6))
  objs=ndimage.find_objects(lab)
  comps=[(i+1,sl) for i,sl in enumerate(objs) if (lab[sl]==i+1).sum()>=3000]
  comps.sort(key=lambda c:(round(c[1][0].stop/120),c[1][1].start))
  assert len(comps)==len(names),(path,len(comps))
  # Bodenlinie je Reihe
  rowkey=lambda sl: round(sl[0].stop/120)
  ground={}
  for idx,sl in comps:
    k=rowkey(sl); ground[k]=max(ground.get(k,0), sl[0].stop-6)
  out=[]
  for (idx,sl),name,mode in zip(comps,names,centroid_modes):
    y0,y1,x0,x1=sl[0].start,sl[0].stop,sl[1].start,sl[1].stop
    gy=ground[rowkey(sl)]
    region=(lab[y0:y1,x0:x1]==idx)
    d=dist[y0:y1,x0:x1]; b=bri[y0:y1,x0:x1]; ne=neutral[y0:y1,x0:x1]
    ys=np.arange(y0,y1)[:,None]
    a=region&(d>=16)&~(ne&(b>110)&(ys>gy-16))
    for it in range(2):
      edge=a&(~np.roll(a,1,0)|~np.roll(a,-1,0)|~np.roll(a,1,1)|~np.roll(a,-1,1))
      a[edge&ne&(b>180)]=False
    # kleine Splitter entfernen
    l2,n2=ndimage.label(a); sizes=ndimage.sum(a,l2,range(1,n2+1))
    for j,s in enumerate(sizes):
      if s<60: a[l2==j+1]=False
    rgba=np.dstack([im[y0:y1,x0:x1],a*255]).astype(np.uint8)
    ys_,xs_=np.where(a); top,bot,left,right=ys_.min(),ys_.max(),xs_.min(),xs_.max()
    crop=Image.fromarray(rgba[top:bot+1,left:right+1],'RGBA')
    # Ankerpunkt
    aa=a[top:bot+1,left:right+1]
    if mode=='feet':
      hh=aa.shape[0]; band=aa[int(hh*0.9):]
      xs=np.where(band)[1]; ax=(xs.min()+xs.max())/2
    elif mode=='head':
      hh=aa.shape[0]; band=aa[:int(hh*0.15)]; ax=np.where(band)[1].mean()-6
    else:
      ax=np.where(aa)[1].mean()
    fy=(gy-(y0+top))
    w,h=crop.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    small=crop.resize((nw,nh),Image.LANCZOS); arr=np.array(small)
    arr[...,3]=np.where(arr[...,3]>100,255,0)
    rgbf=np.clip((arr[...,:3].astype(float)-128)*1.12+128+18,0,255); arr[...,:3]=rgbf.astype(np.uint8)
    out.append((name,Image.fromarray(arr,'RGBA'),round(ax*scale),round(fy*scale)))
  return out
# Originale 3 Posen
orig=np.array(Image.open('sheet.png'))
OM=[{'x': 0, 'w': 44, 'h': 65, 'ax': 25, 'fy': 65}, {'x': 46, 'w': 55, 'h': 60, 'ax': 32, 'fy': 60}, {'x': 103, 'w': 63, 'h': 50, 'ax': 29, 'fy': 50}]
allf=[]
for nm,m in zip(['idle','dash','lunge'],OM):
  allf.append((nm,Image.fromarray(orig[:m['h'],m['x']:m['x']+m['w']],'RGBA'),m['ax'],m['fy']))
allf+=frames_from('sheet_24d74256.jpg',['block','hurt','stagger','fall','dead','flask','drink'],0.218,['feet','feet','feet','all','all','feet','feet'])
allf+=frames_from('sheet_3516b426.jpg',['atk0','atk1','atk2'],0.150,['feet','feet','feet'])
allf+=frames_from('sheet_61a57590.jpg',['roll0','roll1','roll2','roll3'],0.196,['feet','all','all','feet'])
allf+=frames_from('sheet_e4f53fe5.jpg',['walk0','walk1','walk2','walk3','walk4','walk5'],0.213,['head']*6)
# Atlas packen (Zeilen bis 600 px)
meta={};x=y=rowh=0;MAXW=620;placed=[]
for nm,img,ax,fy in allf:
  if x+img.width>MAXW: x=0;y+=rowh+2;rowh=0
  placed.append((img,x,y)); meta[nm]={'x':x,'y':y,'w':img.width,'h':img.height,'ax':int(ax),'fy':int(fy)}
  x+=img.width+2; rowh=max(rowh,img.height)
atlas=Image.new('RGBA',(MAXW,y+rowh),(0,0,0,0))
for img,px,py in placed: atlas.paste(img,(px,py))
atlas.save('atlas.png',optimize=True)
buf=io.BytesIO(); atlas.save(buf,'PNG',optimize=True); open('atlas.b64','w').write(base64.b64encode(buf.getvalue()).decode())
json.dump(meta,open('atlas.json','w'))
print(json.dumps(meta)); print(len(buf.getvalue()))
# Vorschau: alle Frames auf gemeinsamer Bodenlinie mit Ankerstrich
pw=sum(m['w']+20 for m in meta.values()); prev=Image.new('RGBA',(pw,110),(40,36,44,255)); px=10
from PIL import ImageDraw
dr=ImageDraw.Draw(prev)
for nm,img,ax,fy in allf:
  m=meta[nm]; prev.alpha_composite(img,(px,95-m['fy'])); dr.line([(px+m['ax'],96),(px+m['ax'],104)],fill=(255,80,80,255)); px+=m['w']+20
dr.line([(0,95),(pw,95)],fill=(90,90,110,255))
prev=prev.resize((prev.width*3,prev.height*3),Image.NEAREST); prev.save('atlas_preview.png'); print(prev.size)
