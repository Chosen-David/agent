"""Exact teaching figures; no measured/model data. Run with python render_figures.py."""
from pathlib import Path
import json
import platform
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'svg.fonttype': 'none', 'axes.spines.top': False,
                     'axes.spines.right': False})
BLUE, ORANGE, DARK, GREY = '#226BA6', '#C36B16', '#202B3A', '#CCD2D9'
a = np.array([.50, .25, .15, .10])
S = [0, 2]
A = np.array([[1, 1], [0, 1]])
x = np.array([1, 2])
assert np.isclose(a.sum(), 1)
assert np.isclose(a[S].sum(), .65)
assert np.isclose(a[[0, 1]].sum(), .75)
assert np.array_equal(A @ x, [3, 2])
assert np.array_equal(A @ x, A[:, 0] + 2*A[:, 1])

def save(fig, name):
    for suffix in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{suffix}', dpi=150, facecolor='white')
    plt.close(fig)
    with Image.open(OUT / f'{name}.png') as im:
        preview = im.resize((720, round(im.height*720/im.width)), Image.Resampling.LANCZOS)
        preview.save(OUT / f'{name}_720.png')

fig, axs = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={'width_ratios':[1.2, 1]})
fig.subplots_adjust(left=.07, right=.98, top=.78, bottom=.23, wspace=.35)
fig.suptitle('Attention mass: select positions, then add their weights', y=.96, fontsize=16, weight='bold')
ax = axs[0]
bars=ax.bar(range(4), a, color=[BLUE if i in S else GREY for i in range(4)], width=.65)
for i, b in enumerate(bars):
    if i in S: b.set_hatch('//'); b.set_edgecolor('white')
    ax.text(i,a[i]+.015, f'{a[i]:.2f}', ha='center', va='bottom', color=DARK)
ax.set(xticks=range(4), xlabel='Token index', ylabel='Target-layer attention weight', ylim=(0,.6))
ax.set_title('P1  Same query / head', loc='left', fontsize=13)
ax.text(.5,-.27,'Selected positions: S = {0, 2}',transform=ax.transAxes,ha='center',color=BLUE)
ax=axs[1]
left=0
for value, label, color, hatch in [(.65,'S: 65%',BLUE,'//'),(.35,'Other: 35%',GREY,None)]:
    ax.barh(0,value,left=left,color=color,height=.45,hatch=hatch,edgecolor='white')
    ax.text(left+value/2,0,label,ha='center',va='center',color='white' if color==BLUE else DARK,fontweight='bold')
    left+=value
ax.set(xlim=(0,1), ylim=(-.65,.65), yticks=[],xticks=[0,.5,1],xlabel='Fraction of total attention (total = 1)')
ax.spines['left'].set_visible(False)
ax.set_title('P2  Add selected weights', loc='left', fontsize=13)
ax.text(.5,.81,'0.50 + 0.15 = 0.65', transform=ax.transAxes,ha='center',fontsize=15,color=BLUE)
fig.text(.5,.035,'Teaching data supplied in the question; blue + hatching = selected tokens.',ha='center',fontsize=11,color=DARK)
save(fig,'attention_mass')

def arrow(ax,start,end,color,ls='-',lw=2.6):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=15,
                                linewidth=lw,color=color,linestyle=ls,zorder=4))

fig,axs=plt.subplots(1,2,figsize=(10,5.8))
fig.subplots_adjust(left=.065,right=.98,top=.78,bottom=.18,wspace=.24)
fig.suptitle('A maps basis vectors; linearity maps every combination',y=.96,fontsize=16,weight='bold')
fig.text(.5,.865,r'$A=\left[\, (1,0)\quad(1,1)\,\right] \qquad x=e_1+2e_2$',ha='center',fontsize=16)
for k,ax in enumerate(axs):
    ax.set_aspect('equal'); ax.set_xlim(-.45,3.65); ax.set_ylim(-.45,2.7)
    ax.set_xticks([0,1,2,3]); ax.set_yticks([0,1,2]); ax.tick_params(labelsize=10)
    ax.set_xlabel('Horizontal coordinate'); ax.set_ylabel('Vertical coordinate')
    ax.axhline(0,color='#8D98A6',lw=.8); ax.axvline(0,color='#8D98A6',lw=.8)
    T = np.eye(2) if k==0 else A
    for i in range(-3,5):
        p=T@np.array([[i,i],[-3,4]])
        ax.plot(p[0],p[1],color='#E0E5EB',lw=.7,zorder=0)
        p=T@np.array([[-3,4],[i,i]])
        ax.plot(p[0],p[1],color='#E0E5EB',lw=.7,zorder=0)
    e1,e2=T[:,0],T[:,1]
    end=T@x
    arrow(ax,[0,0],end,DARK,lw=2)
    arrow(ax,[0,0],e1,BLUE)
    arrow(ax,[0,0],e2,ORANGE)
    arrow(ax,e1,e1+e2,ORANGE,ls='--',lw=2)
    arrow(ax,e1+e2,end,ORANGE,ls='--',lw=2)
    ax.scatter(*end,color=DARK,s=32,zorder=5)
axs[0].set_title('P1  Before: 1 step + 2 steps',loc='left',fontsize=12)
axs[0].text(.4,-.32,r'$e_1$',color=BLUE,fontsize=14)
axs[0].text(-.34,.95,r'$e_2$',color=ORANGE,fontsize=14)
axs[0].text(1.12,2.12,r'$x=(1,2)$',color=DARK,fontsize=14)
axs[1].set_title('P2  After: same coefficients',loc='left',fontsize=12)
axs[1].text(.32,-.32,r'$Ae_1$',color=BLUE,fontsize=14)
axs[1].text(.24,1.16,r'$Ae_2$',color=ORANGE,fontsize=14)
axs[1].text(2.08,2.18,r'$Ax=(3,2)$',color=DARK,fontsize=14)
fig.text(.5,.07,'Blue: first basis vector  |  Orange: second basis vector  |  Dark: total vector',ha='center',fontsize=11)
fig.text(.5,.03,'Dashed arrows repeat the second basis vector from a new starting point. Exact teaching geometry.',ha='center',fontsize=10)
save(fig,'linear_basis')

checks = {'kind':'exact teaching arithmetic, not model measurements',
 'attention_total':float(a.sum()),'selected_indices':S,'mass':float(a[S].sum()),
 'target_top2_mass':float(a[[0,1]].sum()),'relative_to_top2':float(a[S].sum()/a[[0,1]].sum()),
 'Ae1':A[:,0].tolist(),'Ae2':A[:,1].tolist(),'x':x.tolist(),'Ax':(A@x).tolist(),
 'environment':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
 'checks':'All five arithmetic/identity assertions passed. Visual check is recorded separately.'}
(OUT/'numeric_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
