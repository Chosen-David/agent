import csv

def draw(fig, rect, source):
    rows=list(csv.DictReader(source.open()))
    x,y,w,h=rect
    axes=[fig.add_axes((x,y,w*.68,h)),fig.add_axes((x+w*.83,y,w*.17,h))]
    for ax,scope in zip(axes,['end_to_end','kernel_only']):
        data=[r for r in rows if r['scope']==scope]
        for i,row in enumerate(data):
            for field,offset,color,marker in [('baseline_ms',.13,'#59636E','s'),('candidate_ms',-.13,'#007A94','o')]:
                v=float(row[field]); ax.scatter(v,i+offset,s=24,c=color,marker=marker,zorder=3)
                ax.annotate(f'{v:g}',(v,i+offset),xytext=(5,0),textcoords='offset points',fontsize=7.5,va='center')
        ax.set_yticks(range(len(data)),[r['workload'].capitalize() for r in data],fontsize=8)
        ax.set_ylim(-.5,len(data)-.5); ax.invert_yaxis()
        ax.set_xlim(0,250 if scope=='end_to_end' else 30)
        ax.set_xticks([0,100,200] if scope=='end_to_end' else [0,10,20,30])
        ax.set_xlabel('Time (ms)',fontsize=8)
        ax.set_title('End-to-end' if scope=='end_to_end' else 'Kernel only',fontsize=8.5,loc='left',pad=8)
        ax.grid(axis='x',color='#E0E4E7',linewidth=.6); ax.set_axisbelow(True)
        ax.tick_params(axis='both',length=0,labelsize=7.5,pad=5)
        for sp in ax.spines.values(): sp.set_visible(False)
    return axes
