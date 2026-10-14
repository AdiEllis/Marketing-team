from PIL import Image, ImageFilter
import numpy as np, sys, os
# Usage: python3 -I studio/tools/extract_logo.py <logo.jpg on dark/checker bg> [out_dir=studio/assets]
# -> logo_light.png (cream 'אבן' for dark bg) + logo_alpha.png (charcoal 'אבן' for light bg), gold 'ועץ', real alpha
outdir=sys.argv[2] if len(sys.argv)>2 else 'studio/assets'
a=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
r,g,b=a[...,0],a[...,1],a[...,2]
gold=(r-b)>30
ag=np.clip((r-60)/(200-60),0,1)
ay=np.clip((a.max(-1)-44)/(62-44),0,1)
alpha=np.where(gold,ag,ay)
# supersample for smooth edges
A=Image.fromarray((alpha*255).astype('uint8')).filter(ImageFilter.MedianFilter(5))
A=A.resize((A.width*2,A.height*2),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
A=np.asarray(A).astype(float)/255; A=np.clip((A-0.5)*2.2+0.5,0,1)
G=Image.fromarray(gold.astype('uint8')*255).resize((A.shape[1],A.shape[0]),Image.LANCZOS)
G=(np.asarray(G)>127)
ys,xs=np.where(A>0.5); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max(); pad=30
for gray,name in [([63,64,68],'alpha'),([243,237,228],'light')]:
  out=np.zeros(A.shape+(4,),'uint8')
  out[...,:3]=np.where(G[...,None],np.array([213,167,89]),np.array(gray))
  out[...,3]=(A*255).astype('uint8')
  im=Image.fromarray(out,'RGBA').crop((x0-pad,y0-pad,x1+pad,y1+pad)); w=1100
  im.resize((w,round(im.height*w/im.width)),Image.LANCZOS).save(os.path.join(outdir,f'logo_{name}.png'),optimize=True)
