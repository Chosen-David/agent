"""EXPL-SOFTMAX-001 input v1. Theoretical calculation; no experimental data.
Reproduce: python draw_softmax_temperature.py
Requires existing numpy and matplotlib. All outputs stay beside this script.
"""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(ROOT / 'mplconfig')
os.environ['XDG_CACHE_HOME'] = str(ROOT / 'cache')
import json, csv, math
from decimal import Decimal, localcontext
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_bold_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
regular = FontProperties(fname=font_path, family='Noto Sans CJK JP')
bold = FontProperties(fname=font_bold_path, family='Noto Sans CJK JP', weight='bold')
plt.rcParams.update({'svg.fonttype': 'none', 'font.family': 'DejaVu Sans',
                     'axes.unicode_minus': False, 'mathtext.fontset': 'dejavusans'})
z = np.array([2., 1., 0.])
temperatures = [0.5, 1., 2.]
rows = []
with localcontext() as ctx:
    ctx.prec = 60
    for T in temperatures:
        logits = z/T
        e = np.exp(logits-logits.max())
        p = e/e.sum()
        # Independent high-precision evaluation of the stated (unshifted) formula.
        exact_e = [(Decimal(str(v))/Decimal(str(T))).exp() for v in z]
        exact_p = [q/sum(exact_e) for q in exact_e]
        assert np.allclose(p, [float(v) for v in exact_p], rtol=0, atol=5e-16)
        assert abs(float(p.sum())-1) < 5e-16
        assert p[0] > p[1] > p[2] > 0
        assert abs(math.log(p[0]/p[1])-1/T) < 1e-15
        rows.append({'T':T, 'logits':z.tolist(), 'scaled_logits':logits.tolist(),
                     'probabilities':p.tolist(),
                     'probabilities_decimal_60_digits':[str(x) for x in exact_p],
                     'display_4dp':[f'{v:.4f}' for v in p],
                     'sum':float(p.sum()), 'ln_p1_over_p2':math.log(p[0]/p[1])})

colors = ['#2878B5', '#D8792B', '#8561B5']
fig = plt.figure(figsize=(7.2, 4.9), facecolor='#FFFFFF')
fig.text(.052, .935, '温度越大，概率分布越平缓', fontsize=20,
         fontproperties=bold, color='#152738')
fig.text(.052, .879, '固定 logits = [2, 1, 0]；仅改变正温度 T', fontsize=12,
         fontproperties=regular, color='#35495B')
fig.text(.052, .825, r'$p_i(T)=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)},\quad T>0$',
         fontsize=15, color='#152738')
fig.text(.948, .827, '理论计算', ha='right', fontsize=10,
         fontproperties=regular, color='#647587')
# Identical scales and repeated category labels avoid relying on color alone.
lefts=[.083, .398, .713]
for k, (left, row) in enumerate(zip(lefts, rows)):
    ax=fig.add_axes([left, .285, .237, .425])
    p = row['probabilities']
    ax.set_ylim(0,1)
    ax.set_xlim(-.55,2.55)
    ax.set_yticks([0, .25, .5, .75, 1.])
    ax.set_yticklabels(['0', '.25', '.50', '.75', '1.00'], fontsize=9)
    ax.tick_params(axis='y', length=0, pad=5, colors='#647587')
    ax.set_xticks([0,1,2])
    ax.set_xticklabels(['z=2','z=1','z=0'], fontsize=11)
    ax.tick_params(axis='x', length=0, pad=7, colors='#35495B')
    for side in ['top','right','left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#AEBAC5')
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#E6EBF0', linewidth=.7)
    ax.axhline(1/3, color='#7C8791', linewidth=1, linestyle=(0,(3,3)), zorder=2)
    ax.bar(range(3), p, width=.63, color=colors, zorder=3)
    for x, val in enumerate(p):
        ax.text(x, val+.024, f'{val:.4f}', ha='center', va='bottom',
                fontsize=10.2, fontweight='medium', color='#152738')
    ax.set_title(f'T = {row["T"]:g}', fontsize=15, weight='bold', pad=12, color='#152738')
    if k == 0:
        ax.text(-.28, 1.02, '概率', transform=ax.transAxes, fontsize=10,
                fontproperties=regular, color='#647587')

fig.text(.052, .191, '虚线为 1/3；概率保留 4 位小数，相加可能略偏离 1。',
         fontsize=11, fontproperties=regular, color='#526579')
fig.text(.052, .125, r'对数概率比：$\ln(p_i/p_j)=(z_i-z_j)/T$；T 越大，差距越小。',
         fontsize=11.5, fontproperties=regular, color='#243C50')
fig.text(.052, .066, r'排序始终 $p_1>p_2>p_3$；$T\to\infty$ 时，各项趋于 $1/3$。',
         fontsize=11.5, fontproperties=regular, color='#243C50')
fig.savefig(ROOT/'softmax_temperature.png', dpi=100, facecolor='white')
fig.savefig(ROOT/'softmax_temperature_2x.png', dpi=200, facecolor='white')
fig.savefig(ROOT/'softmax_temperature.svg', facecolor='white')
plt.close(fig)

metadata={'explanation_id':'EXPL-SOFTMAX-001', 'input_version':'v1',
          'route':'data_visualization', 'data_kind':'theoretical',
          'definition':'p_i(T)=exp(z_i/T)/sum_j exp(z_j/T), T>0',
          'category_order':['p1 (z=2)','p2 (z=1)','p3 (z=0)'],
          'colors':colors, 'rows':rows,
          'step_panel_mapping':{'S1':'P1: title and fixed-input/formula block',
              'S2':'P2: the three matched-scale bar panels',
              'S3':'P3: dashed uniform reference and log-odds/order/limit footer'}}
(ROOT/'softmax_temperature_data.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
with (ROOT/'softmax_temperature_data.csv').open('w', newline='') as f:
    w=csv.writer(f); w.writerow(['T','p1_z2','p2_z1','p3_z0','sum'])
    for row in rows: w.writerow([row['T'],*row['probabilities'],row['sum']])
print(json.dumps(rows, ensure_ascii=False, indent=2))
