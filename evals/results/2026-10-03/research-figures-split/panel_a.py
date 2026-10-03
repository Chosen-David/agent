import json
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def draw(fig, rect, source):
    spec=json.loads(source.read_text())
    ax=fig.add_axes(rect); ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
    pos={'a':(.105,.55),'b':(.105,.15),'sum':(.355,.35),'softmax':(.595,.35),'v':(.855,.79),'output':(.855,.35)}
    labels={'a':'Path A logits a','b':'Path B logits b','sum':'z = a + b','softmax':'p = softmax(z)','v':'Fixed values V','output':r'$y = p^{T}V$'}
    w,h=.19,.23
    for node in spec['nodes']:
        k=node['id']; x,y=pos[k]
        fill='#E6F0F4' if k in ('sum','softmax','output') else '#F2F3F4'
        box=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.006,rounding_size=0.02',facecolor=fill,edgecolor='#51636F',linewidth=.85)
        box.set_gid('node_'+k); ax.add_patch(box)
        ax.text(x,y,labels[k],ha='center',va='center',fontsize=8.2)
    for s,t in spec['edges']:
        x1,y1=pos[s]; x2,y2=pos[t]
        if s=='v': start=(x1,y1-h/2-.01); end=(x2,y2+h/2+.01)
        else: start=(x1+w/2+.008,y1); end=(x2-w/2-.008,y2)
        arrow=FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=9,linewidth=.9,color='#35444D',connectionstyle='arc3,rad=0')
        arrow.set_gid('edge_'+s+'_'+t); ax.add_patch(arrow)
    return ax
