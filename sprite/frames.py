from PIL import Image, ImageEnhance
import numpy as np, json, base64, io
im=np.array(Image.open('cut_full.png')).copy()
# Bodenwirbel bei Pose 3 entfernen
reg=im[425:565,1160:1262]; rgb=reg[...,:3].astype(int)
neu=(rgb.max(2)-rgb.min(2))<14; bri=rgb.mean(2)
reg[...,3][neu&(bri>100)]=0
rgbA=im[...,:3].astype(int); dA=np.abs(rgbA-213).max(2); im[...,3][(dA<12)]=0
full=Image.fromarray(im,'RGBA')
boxes=[(32,105,356,590),(371,133,775,582),(795,212,1260,587)]
feet=[585,577,582]; anchors=[215,610,1010]
SCALE=1/7.4
frames=[];meta=[]
x=0;sheet_h=0
for (x0,y0,x1,y1),fy,ax in zip(boxes,feet,anchors):
  crop=full.crop((x0,y0,x1,fy+3))
  w,h=crop.size; nw,nh=max(1,round(w*SCALE)),max(1,round(h*SCALE))
  small=crop.resize((nw,nh),Image.LANCZOS)
  a=np.array(small); al=a[...,3]
  a[...,3]=np.where(al>100,255,0)
  rgbf=a[...,:3].astype(float)
  rgbf=np.clip((rgbf-128)*1.12+128+18,0,255)   # etwas heller/kontrastreicher fürs dunkle Spiel
  a[...,:3]=rgbf.astype(np.uint8)
  small=Image.fromarray(a,'RGBA')
  frames.append(small)
  meta.append({'x':x,'w':nw,'h':nh,'ax':round((ax-x0)*SCALE),'fy':round((fy-y0)*SCALE)})
  x+=nw+2; sheet_h=max(sheet_h,nh)
sheet=Image.new('RGBA',(x,sheet_h),(0,0,0,0))
for f,m in zip(frames,meta): sheet.paste(f,(m['x'],0))
sheet.save('sheet.png',optimize=True)
buf=io.BytesIO(); sheet.save(buf,'PNG',optimize=True)
b64=base64.b64encode(buf.getvalue()).decode()
open('sheet.b64','w').write(b64)
print(meta, len(b64))
big=sheet.resize((sheet.width*5,sheet.height*5),Image.NEAREST); bg=Image.new('RGBA',big.size,(40,36,44,255)); bg.alpha_composite(big); bg.save('sheet_preview.png')
