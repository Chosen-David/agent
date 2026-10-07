"""EXPL-ROPE-001 • input v1 • theoretical teaching schematic.
Reproduce with: python draw_rope_pairs.py
No measured data; two angular frequencies are chosen for easy arithmetic.
"""
from pathlib import Path
import os, math, json
OUT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(OUT / '.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Arc
from matplotlib.font_manager import FontProperties
from PIL import Image
matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
R = FontProperties(family=['Noto Sans CJK JP', 'DejaVu Sans'])
B = FontProperties(family=['Noto Sans CJK JP', 'DejaVu Sans'], weight='bold')
W,H = 720,1130
fig = plt.figure(figsize=(W/100,H/100),dpi=100)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
BG='#F5F7FA'; INK='#173044'; MUTED='#536B7C'; LINE='#D9E1E7'
GREEN='#18845F'; GREEN_D='#126B4D'; GREEN_LIGHT='#E7F5EE'; BLUE='#56758E'; BLUE_LIGHT='#EDF2F6'
fig.patch.set_facecolor(BG)
def text(x,y,s,size=18,color=INK,weight='regular',ha='left',va='center'):
    # sizes are specified in display pixels, converted to typographic points.
    return ax.text(x,y,s,fontsize=size*.72,color=color,fontproperties=B if weight=='bold' else R,ha=ha,va=va)
def box(x,y,w,h,fill='#FFFFFF',edge='none',r=16,lw=1.2):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',linewidth=lw,facecolor=fill,edgecolor=edge);ax.add_patch(p);return p
def line(x1,y1,x2,y2,color=LINE,lw=1.4,ls='-'):
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,solid_capstyle='round')
def arrow(x1,y1,x2,y2,color=INK,lw=2.2,ms=12,style='-|>',ls='-'):
    a=FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=ms,linewidth=lw,color=color,linestyle=ls,shrinkA=0,shrinkB=0);ax.add_patch(a);return a
def section(y,n,title):
    box(24,y,672,54,fill='#FFFFFF',r=18)
    ax.add_patch(Circle((53,y+28),15,facecolor=INK,edgecolor='none'))
    text(53,y+28,str(n),18,'#FFFFFF','bold',ha='center')
    text(81,y+28,title,23,weight='bold')

def orbit(cx,cy,r,theta,cl,axisnames,anglelabel):
    ax.add_patch(Circle((cx,cy),r,edgecolor=LINE,facecolor='none',linewidth=1.15))
    line(cx-r-10,cy,cx+r+14,cy,color=LINE,lw=1.2)
    line(cx,cy+r+10,cx,cy-r-12,color=LINE,lw=1.2)
    arrow(cx,cy,cx+r,cy,color='#9AABB6',lw=1.9,ms=10,ls='--')
    ex=cx+r*math.cos(theta); ey=cy-r*math.sin(theta)
    arrow(cx,cy,ex,ey,color=cl,lw=3.2,ms=14)
    ax.add_patch(Circle((cx,cy),3,facecolor=cl,edgecolor='none'))
    t=[i*theta/40 for i in range(41)]
    rr=r*.37
    ax.plot([cx+rr*math.cos(a) for a in t],[cy-rr*math.sin(a) for a in t],color=cl,lw=1.6)
    a=theta*.72
    if theta < math.pi/3:
        text(cx+51,cy-53,anglelabel,17,cl,ha='center')
    else:
        text(cx+r*.65*math.cos(a),cy-r*.65*math.sin(a),anglelabel,17,cl,ha='center')
    text(cx+r+23,cy+2,axisnames[0],17,MUTED,ha='center')
    text(cx,cy-r-25,axisnames[1],17,MUTED,ha='center')

text(32,40,'RoPE 的低频，为什么要成对留？',28,weight='bold')
text(33,80,'这里的一对，是同一个 token 的两个通道坐标。',18,MUTED)

# S1 -> P1: frequency is assigned to a full pair.
box(24,115,672,365,fill='#FFFFFF',r=20)
section(115,1,'频率属于一对坐标')
box(43,181,300,274,fill=BLUE_LIGHT,r=14)
box(377,181,300,274,fill=GREEN_LIGHT,edge='#ACD9C3',r=14)
text(193,208,'高频对  (x₁, x₂)',21,BLUE,'bold',ha='center')
text(527,208,'低频对  (x₃, x₄)',21,GREEN_D,'bold',ha='center')
text(193,241,'ω = π/2 · 每步 90°',18,BLUE,ha='center')
text(527,241,'ω = π/6 · 每步 30°',18,GREEN_D,ha='center')
orbit(180,351,57,math.pi/2,BLUE,('x₁','x₂'),'90°')
orbit(514,351,57,math.pi/6,GREEN,('x₃','x₄'),'30°')
text(193,433,'起点都为 (1, 0)',17,MUTED,ha='center')
box(413,415,228,32,fill=GREEN,r=8)
text(527,431,'整对保留：x₃ 和 x₄',18,'#FFFFFF','bold',ha='center')

# S2 -> P2: numerical rotation and coordinate projection.
box(24,498,672,383,fill='#FFFFFF',r=20)
section(498,2,'拆一半，就不再是完整旋转')
text(49,566,'旋转时，两个坐标会相互混合。',18,MUTED)
box(49,594,124,51,fill=GREEN_LIGHT,r=10)
text(111,620,'(1, 0)',22,GREEN_D,ha='center')
arrow(187,620,287,620,color=GREEN,lw=2,ms=12)
text(237,600,'转 30°',16,GREEN_D,ha='center')
box(303,594,345,51,fill=GREEN_LIGHT,r=10)
text(475,620,'(0.866, 0.500)',22,GREEN_D,'bold',ha='center')
# At radius 140 the vector end is exactly the (cos30,sin30) location.
cx,cy,r=98,812,140
ex,ey=cx+r*math.cos(math.pi/6),cy-r*.5
arrow(cx-18,cy,cx+r+27,cy,color='#99ABB6',lw=1.3,ms=8)
arrow(cx,cy+17,cx,cy-112,color='#99ABB6',lw=1.3,ms=8)
text(cx+r+31,cy+2,'x₃',18,MUTED)
text(cx,cy-128,'x₄',18,MUTED,ha='center')
arrow(cx,cy,ex,ey,color=GREEN,lw=3.2,ms=14)
line(ex,ey,ex,cy,color=GREEN,lw=1.5,ls='--')
line(cx,ey,ex,ey,color='#A9CABB',lw=1.2,ls='--')
ax.add_patch(Circle((ex,cy),4,facecolor=GREEN,edgecolor='none'))
text(ex,cy+28,'0.866',17,GREEN_D,ha='center')
text(cx-9,ey,'0.500',16,GREEN_D,ha='right')
text(169,694,'二维向量',17,GREEN_D,ha='center')
# Right comparison is redundant to color and explains the cut.
box(340,686,306,65,fill=GREEN_LIGHT,r=10)
text(358,706,'保留 (x₃, x₄)',19,GREEN_D,'bold')
text(358,731,'完整保留这个旋转块',17,GREEN_D)
box(340,765,306,81,fill='#F1F3F5',edge='#D9DFE4',r=10)
text(358,787,'只留 x₃，丢掉 x₄',19,INK,'bold')
text(358,820,'0.866  →  只剩投影',19,MUTED)

# S3 -> P3: no predefined spectral ordering in NoPE.
box(24,899,672,181,fill='#FFFFFF',r=20)
section(899,3,'NoPE：没有这张频率表')
text(49,969,'普通通道',18,MUTED)
for i,x in enumerate((197,294,391,488),1):
    box(x,948,78,40,fill=BLUE_LIGHT,r=8)
    text(x+39,968,f'x{str(i).translate(str.maketrans("1234","₁₂₃₄"))}',21,INK,ha='center')
text(49,1013,'通道序号 ≠ 高频到低频的排序',20,INK,'bold')
text(49,1050,'所以不能直接照着通道编号“选低频”。',18,MUTED)

text(32,1104,'教学示意：π/2、π/6 为方便计算的频率，并非 RoPE 默认参数。',15,MUTED)
fig.savefig(OUT/'rope_pairs.png',dpi=200,facecolor=BG)
fig.savefig(OUT/'rope_pairs.svg',facecolor=BG)
fig.savefig(OUT/'rope_pairs_preview_720.png',dpi=100,facecolor=BG)
plt.close(fig)
# Separate numeric verification from rendering.
rot=[[math.cos(math.pi/6),-math.sin(math.pi/6)],[math.sin(math.pi/6),math.cos(math.pi/6)]]
v=[1.0,0.0]
out=[sum(a*b for a,b in zip(row,v)) for row in rot]
assert abs(out[0]-.8660254037844387)<1e-12
assert abs(out[1]-.5)<1e-12
assert abs(sum(z*z for z in out)-1)<1e-12
assert all(abs(v)>0 for row in rot for v in row), 'Both rotated coordinates depend on both input coordinates at 30 degrees.'
assert abs(math.pi/2*180/math.pi-90)<1e-12
assert abs(math.pi/6*180/math.pi-30)<1e-12
qa={'explanation_id':'EXPL-ROPE-001','input_version':'v1','route':'diagram','kind':'theoretical teaching schematic','rotation_30_degrees':rot,'rotated_point':out,'pair_squared_norm':sum(z*z for z in out),'projection_squared_norm':out[0]**2,'both_rotation_outputs_depend_on_both_inputs':True,'files':{p.name:list(Image.open(p).size) for p in (OUT/'rope_pairs.png',OUT/'rope_pairs_preview_720.png')}}
(OUT/'numeric_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qa,ensure_ascii=False,indent=2))
