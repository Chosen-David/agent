import json, hashlib, copy
from pathlib import Path
from datetime import datetime, timezone
P=Path('/tmp/agent-forward-travel-v2/travel-planner'); O=P/'outputs'
src=P/'inputs/travel.json'; data=json.loads(src.read_text()); checked=datetime.now(timezone.utc).isoformat()
def ts(t): return data['date']+'T'+t+':00+08:00'
def meta(rev,deps,built=None): return dict(built_from_revision=built or rev,validated_for_revision=rev,depends_on=deps,validity='current')
def price(lo,hi,unit,quantity,original=None):
    p=dict(min=lo,max=hi,currency='CNY',unit=unit,quantity=quantity,includes=[],excludes=['未提供的额外服务'],source_status='reference',checked_at=checked)
    if original:p['original_unit']=original
    return p
unknowns=[
 {'unknown_id':'u_currency','content':'币种未给；本报告暂用 CNY，需确认。','owner':'user'},
 {'unknown_id':'u_room','content':'Hotel H 用房可用已给定；房费、是否已支付、午休是否新增收费未给。未按零计入。','owner':'user'},
 {'unknown_id':'u_routes','content':'城市、入口、上车点、实际线路、替代交通费用和实时拥堵未给；以门牌为合成路线端点，每段时长暂视为含步行候车的全程。','owner':'fixture_author'},
 {'unknown_id':'u_weather','content':'无天气资料、预警或室内外信息；不能验证实际天气适用性。','owner':'fixture_author'},
 {'unknown_id':'u_services','content':'排队、最后接客、离店余量、写真准备时长及额外收费未知。暂留午餐前10分钟、用餐后5分钟；写真预约视为含准备的完整服务，提前10分钟报到，结束后5分钟离场。','owner':'fixture_author'},
 {'unknown_id':'u_return','content':'18:00仅为可活动时间终点，无车站/航班要求；假设当天11:00从 Hotel H 出发并最终回 Hotel H。','owner':'user'},
 {'unknown_id':'u_payment','content':'写真已有用户确认预约，但未给支付状态、套餐附加费用或总预算上限。已知报价列为计划费用，不认定未付或已付。','owner':'user'}]
entities=[('hotel','Hotel H','1 Test Road'),('lunch','Cafe A','2 Test Road'),('photo','Studio B','3 Test Road')]
base=dict(schema_version='local-travel/v1',trip_id='synthetic-travel-20261004',revision=1,as_of=checked)
base['request_contract']={
 'trip_brief':dict(destination='合成目的地（城市未知）',timezone=data['timezone'],dates={'start':data['date'],'end':data['date']},people=2,anchor={'kind':'hotel','entity_id':'hotel'},arrival=ts('11:00'),departure=ts('18:00'),budget={'min':None,'max':None,'currency':None,'scope':'双人，用户未给上限'},rest_preferences={'default_enabled':True,'midday_minutes':75,'needs_room':True,'walking_tolerance':None},assumptions=['起终点均为 Hotel H','CNY 为预算展示假设','每段通勤为一辆车，给定时长含步行候车','给定通勤价格不因仅修改时长而改变','写真16:00–17:00包含服务准备；无额外付费项目假设']),
 'hard_constraints':[{'constraint_id':'h_available','content':'11:00–18:00 可活动','source':'travel.json:available','user_confirmed':True},{'constraint_id':'h_photo','content':'Studio B 16:00–17:00 用户确认预约，不能改动','source':'travel.json:photo','user_confirmed':True},{'constraint_id':'h_rest','content':'Hotel H 独立午休75分钟，用房可用','source':'travel.json:rest','user_confirmed':True},{'constraint_id':'h_no_booking','content':'不实际预订，不联系商户，仅用合成事实','source':'task.txt / travel.json:amendment','user_confirmed':True}],
 'desired_intents':[{'intent_id':k,'goal':goal,'must_do':True,'acceptance_conditions':cond} for k,goal,cond in [('lunch','Cafe A 午餐','完整60分钟，单个营业窗口，14:00前点单'),('photo','Studio B 写真','保持16:00–17:00预约'),('rest','Hotel H 午休','独立75分钟，不以交通/用餐代替')]],
 'soft_preferences':[], 'unknowns':unknowns, 'acceptance_criteria':['保留三项必须活动','完整午餐在同一营业窗口内，点单不晚于14:00','四段通勤全部计时计价','18:00前回酒店','按人数/整单/整车正确计算费用','缺失信息不伪装已验证']}
base['capabilities']=[{'name':'local_file_read_write_and_python','version':'Python 3 standard library','permission':'本 case 本地读取，outputs 写入','verified_by':'读取 travel.json、生成 JSON/Markdown、执行静态检查','limits':'未联网、未调用地图天气平台、未预订、未生成 Word；无独立研究 Agent'}]
base['sources']=[{'source_id':'s_fixture','url':None,'source_type':'user_supplied_synthetic_fixture','published_at':None,'checked_at':checked,'access_scope':'full','scope':'仅本合成案例，不证明现实商户存在','path':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()}]
base['facts']=[]
for id,claim,val in [('lunch_windows','service_windows',[{'open':ts(a),'close':ts(b)} for a,b in data['lunch']['service_windows']]),('lunch_break','break_windows',[{'open':ts('14:30'),'close':ts('16:00')}]),('lunch_order','last_order',ts('14:00')),('photo_appointment','appointment',{'start':ts('16:00'),'end':ts('17:00')}),('room','room_available',True),('travel_time','each_leg_minutes',20),('travel_price','each_leg_price',[15,25])]:
    entity='lunch' if id.startswith('lunch') else 'photo' if id.startswith('photo') else 'hotel' if id=='room' else 'transport'
    base['facts'].append(dict(fact_id='f_'+id,entity_id=entity,claim=claim,value=val,applies_on=data['date'],timezone=data['timezone'],source_ids=['s_fixture'],checked_at=checked,status='user_confirmed',**meta(1,['s_fixture'])))
base['experiences']=[];base['weather']=[]
base['research_queries']=[dict(query_id='q_local',owner='single_planner',intent_id=None,entity_scope=['hotel','lunch','photo','transport'],required_fields=['addresses','windows','duration','price','appointment','rest'],preferred_sources=['s_fixture'],fallback_sources=[],done_when='已读取所有给定字段，未提供字段列 unknown',status='COMPLETED',input_revision=1)]
base['candidates']=[]
for kind,name,address in entities:
    id='rest' if kind=='hotel' else kind
    p=price(80,100,'per_person',2) if kind=='lunch' else price(300,300,'per_package',1,'per_group') if kind=='photo' else price(None,None,'per_room',None)
    if kind=='hotel':p['source_status']='unknown'
    base['candidates'].append(dict(candidate_id='c_'+id,entity_id=kind,kind='rest' if kind=='hotel' else 'activity',name=name,navigable_address=address,intent_ids=[id],fact_ids=['f_room'] if kind=='hotel' else ['f_lunch_windows','f_lunch_order'] if kind=='lunch' else ['f_photo_appointment'],price=p,duration_minutes={'hotel':75,'lunch':60,'photo':60}[kind],admission='admitted',admission_scope='仅对合成场景给定事实及明示假设准入，非现实出行核验',unknowns=['u_room'] if kind=='hotel' else ['u_services'],**meta(1,['s_fixture'])))
base['selection_plan']=[dict(intent_id=id,primary='c_'+id,alternatives=[],fallbacks=[],basis='输入仅提供一个指定实体；不捏造额外商户或候选',conditions=['实际出行前修复 unknown；本次限合成规划'],**meta(1,['c_'+id])) for id in ['lunch','photo','rest']]
base['open_questions']=[{'unknown_id':u['unknown_id']} for u in unknowns]
base['change_log']=[]

def compose(b,rev):
    b['revision']=rev; dur=20 if rev==1 else 35
    # Stable slot IDs; amendment shifts every affected downstream slot.
    if rev==1: times=[('11:00','11:20'),('11:20','11:30'),('11:30','12:30'),('12:30','12:35'),('12:35','12:55'),('12:55','13:00'),('13:00','14:15'),('14:15','15:30'),('15:30','15:50'),('15:50','16:00'),('16:00','17:00'),('17:00','17:05'),('17:05','17:25'),('17:25','18:00')]
    else: times=[('11:00','11:35'),('11:35','11:45'),('11:45','12:45'),('12:45','12:50'),('12:50','13:25'),('13:25','13:30'),('13:30','14:45'),('14:45','15:15'),('15:15','15:50'),('15:50','16:00'),('16:00','17:00'),('17:00','17:05'),('17:05','17:40'),('17:40','18:00')]
    specs=[('transfer',None,[],'前往 Cafe A'),('buffer',None,[],'午餐报到/候位余量（估计）'),('activity','c_lunch',['lunch'],'午餐，到店后于本块开始时点单'),('buffer',None,[],'午餐离店余量'),('transfer',None,[],'回 Hotel H'),('buffer',None,[],'回房整理'),('rest','c_rest',['rest'],'独立用房午休75分钟'),('buffer',None,[],'酒店机动等候；可继续休息，不计入75分钟'),('transfer',None,[],'前往 Studio B'),('buffer',None,[],'写真提前报到'),('activity','c_photo',['photo'],'既定写真预约'),('buffer',None,[],'写真离场余量'),('transfer',None,[],'回 Hotel H'),('buffer',None,[],'已回酒店，距离18:00的返程余量')]
    b['itinerary']=[]
    for i,((start,end),(kind,cid,intents,label)) in enumerate(zip(times,specs),1):
        b['itinerary'].append(dict(slot_id='s'+str(i),kind=kind,candidate_id=cid,intent_ids=intents,start=ts(start),end=ts(end),description=label,conditions=['合成场景及明示假设'],fact_dependencies=['f_travel_time'] if kind=='transfer' else ['f_lunch_windows','f_lunch_order'] if cid=='c_lunch' else ['f_photo_appointment'] if cid=='c_photo' else ['f_room'] if cid=='c_rest' else [],**meta(rev,['request_contract']+([cid] if cid else []))))
    b['itinerary'][2]['order_at']=b['itinerary'][2]['start']
    legs=[('Hotel H, 1 Test Road','Cafe A, 2 Test Road','去指定午餐；只提供整车交通资料，双人共乘一辆车',1),('Cafe A, 2 Test Road','Hotel H, 1 Test Road','回已知可用房间休息，保证75分钟独立午休',5),('Hotel H, 1 Test Road','Studio B, 3 Test Road','按预约倒推发车，保留10分钟报到余量',9),('Studio B, 3 Test Road','Hotel H, 1 Test Road','按假设回原锚点，保留18:00前机动时间',13)]
    b['commutes']=[dict(commute_id='t'+str(i),from_endpoint=a,to_endpoint=z,entrances='未提供，不能编造入口/上下车点',mode='合成车辆交通（具体车型/叫车方式未知）',route='按给定起终点；道路、线路、方向、换乘未提供',duration_minutes={'min':dur,'max':dur},duration_scope='暂按含步行候车的全程时长；时长外另排活动进出余量',price=price(15,25,'per_car',1,'per_vehicle'),people=2,source_ids=['s_fixture'],status='reference',reason=reason,alternatives='未提供公交/地铁/步行时间费用，不能作真实经济性比较',slot_id='s'+str(slot),**meta(rev,['f_travel_time','f_travel_price'])) for i,(a,z,reason,slot) in enumerate(legs,1)]
    b['budget']=dict(currency='CNY',currency_assumption=True,people=2,lines=[{'item':'午餐','price':price(80,100,'per_person',2),'total_min':160,'total_max':200},{'item':'写真','price':price(300,300,'per_package',1,'per_group'),'total_min':300,'total_max':300},{'item':'交通四段','price':price(15,25,'per_car',4,'per_vehicle'),'quantity_explanation':'1辆车 × 4段；不乘2位乘客','total_min':60,'total_max':100}],known_subtotal={'min':520,'max':600},contingency={'rate_min':0.1,'rate_max':0.2,'min':52,'max':120},known_total_with_contingency={'min':572,'max':720},unknown_items=['u_room','u_payment'],paid_total=None,new_spend_total=None,scope='双人已知计划费用；含10%–20%机动金的部分预算，不是含未知房费/附加费的完整总价。已付与待付状态未知。',**meta(rev,['c_lunch','c_photo','c_rest','t1','t2','t3','t4']))
    b['intent_coverage']=[dict(intent_id=intent,slot_ids=[slot],outcome='satisfied',evidence=detail,scope='合成输入与假设内',**meta(rev,[slot])) for intent,slot,detail in [('lunch','s3','60分钟且离店余量仍在午市内；点单早于14:00'),('photo','s11','16:00–17:00保持用户预约'),('rest','s7','独立75分钟；用房可用')]]
    b['deliverables']=[dict(format='json',path=str(O/f'delivery_bundle_v{rev}.json'),bundle_revision=rev,validity='current',qa_status='limited',checked_pages=None,total_pages=None,limits='结构、时间和算术可检查；现实营业、线路、币种和总费用无法核验',access_check='本地读取成功')]
    b['run_state']={'stages':[dict(stage_id=s,status='COMPLETED',input_revision=rev,depends_on=deps,outputs=outputs,error=None,blocked_reason=None) for s,deps,outputs in [('contract',[],['request_contract']),('local_research',['contract'],['research_queries','facts','candidates']),('admission_selection',['local_research'],['selection_plan']),('compose',['admission_selection'],['itinerary','commutes','budget']),('fidelity_gate',['compose'],['intent_coverage']),('delivery',['fidelity_gate'],['deliverables'])]],'gate':{'synthetic_schedule':'pass','real_world_execution':'limited','reason':'只验收给定合成事实及明示假设，不声称现实商户或完整费用已核验'}}
    return b

v1=compose(base,1)
(O/'delivery_bundle_v1.json').write_text(json.dumps(v1,ensure_ascii=False,indent=2))
v2=copy.deepcopy(v1)
v2['change_log']=[dict(amendment_id='amend_1',from_revision=1,to_revision=2,changed_fields=['facts.f_travel_time.value:20->35'],source='travel.json:amendment',decision=data['amendment'],affected_ids=['f_travel_time','t1','t2','t3','t4','s1','s2','s3','s4','s5','s6','s7','s8','s9','s13','s14','budget','intent_coverage','deliverables'],reason='每段通勤增长15分钟，4段共增长60分钟',invalidated_before_rebuild=['commutes','itinerary','budget','intent_coverage','deliverables'],reused_after_review=['lunch service windows/price','photo appointment/price','room availability','selection_plan','f_travel_price'],followup_tasks=['重算午餐及午休','提前前往写真','重算回酒店时间','重算同价交通总额','重新验收'])]
v2['request_contract']['hard_constraints'].append({'constraint_id':'h_commute_v2','content':'每段通勤改为35分钟，保持写真和午休','source':'travel.json:amendment','user_confirmed':True})
for section in ['facts','candidates','selection_plan']:
    for x in v2[section]:
        x['validated_for_revision']=2
        if x.get('fact_id')=='f_travel_time':
            x['value']=35; x['built_from_revision']=2
v2['research_queries'][0]['revalidated_for_revision']=2
v2=compose(v2,2)
(O/'delivery_bundle_v2.json').write_text(json.dumps(v2,ensure_ascii=False,indent=2))
# This script checks fixture arithmetic and schedule, not live travel evidence.
results=[]
for b in [v1,v2]:
    slots=b['itinerary']; conv=lambda s:datetime.fromisoformat(s)
    assert slots[0]['start']==ts('11:00') and slots[-1]['end']==ts('18:00')
    assert all(a['end']==z['start'] for a,z in zip(slots,slots[1:]))
    assert all(conv(s['start'])<conv(s['end']) for s in slots)
    minute=lambda s:(conv(s['end'])-conv(s['start'])).total_seconds()/60
    assert minute(slots[2])==60 and minute(slots[6])==75
    assert slots[10]['start']==ts('16:00') and slots[10]['end']==ts('17:00')
    assert ts('10:30')<=slots[2]['start'] and slots[3]['end']<=ts('14:30')
    assert slots[2]['order_at']<=ts('14:00')
    assert len(b['commutes'])==4 and all(minute(slots[int(c['slot_id'][1:])-1])==(20 if b['revision']==1 else 35) for c in b['commutes'])
    for line in b['budget']['lines']:
        p=line['price']; assert p['min']*p['quantity']==line['total_min'] and p['max']*p['quantity']==line['total_max']
    assert sum(x['total_min'] for x in b['budget']['lines'])==520
    assert sum(x['total_max'] for x in b['budget']['lines'])==600
    ids={c['candidate_id'] for c in b['candidates']}
    assert all(s['candidate_id'] in ids or s['candidate_id'] is None for s in slots)
    results.append({'revision':b['revision'],'static_checks':'passed','commute_minutes':sum(minute(s) for s in slots if s['kind']=='transfer'),'return_at':slots[12]['end'],'limits':'Synthetic schedule only; not live route, business, price, weather or booking verification.'})
(O/'validation.json').write_text(json.dumps({'input_sha256':base['sources'][0]['sha256'],'checks':results},ensure_ascii=False,indent=2))
lines=['# 合成一日行程：原版与修订版','', '日期：2026-10-04；Asia/Shanghai（UTC+08:00）；2人；11:00–18:00。所有酒店、店铺和路线均为输入中的合成实体，非真实商户推荐。只使用 travel.json，没有联网或预订。', '', '假设11:00从 Hotel H（1 Test Road）出发并返回同处。币种未给，以下暂按 CNY 表示。每段给定通勤视为含步行候车的全程车辆交通；实际入口、道路和交通方式未知。午餐候位留10分钟，进出活动另留5分钟；写真提前10分钟报到，预约60分钟暂视为包含准备。', '', '## 两个版本的时间表', '', '|活动|v1：每段20分钟|v2：每段35分钟|','|---|---|---|']
for a,z in zip(v1['itinerary'],v2['itinerary']):lines.append('|'+a['description']+'|'+a['start'][11:16]+'–'+a['end'][11:16]+'|'+z['start'][11:16]+'–'+z['end'][11:16]+'|')
lines+=['','午餐地址：Cafe A，2 Test Road；写真地址：Studio B，3 Test Road；午休为 Hotel H 房内独立75分钟，用房可用由输入提供。v1在11:30点单，v2在11:45点单，均早于14:00；用餐及离店完整处于10:30–14:30午市。晚市16:00–21:00独立保留，14:30–16:00不安排用餐。', '', '## 逐段通勤与理由','','|起点 → 终点（门牌为已知定位范围）|方式及理由|v1 / v2时长|双人费用|','|---|---|---|---|']
for c in v2['commutes']:lines.append('|'+c['from_endpoint']+' → '+c['to_endpoint']+'|一辆合成车辆；'+c['reason']+'|20 / 35分钟|15–25 CNY/车/单程|')
lines+=['','每段只有给定车辆方案。没有公交、地铁、步行的线路/时长/费用，不能声称车辆最便宜或捏造替代站点；上车点和入口也未提供。四段均计入两版时间表。','', '## 双人预算（两版相同）','','|项目|计价与数量|金额（暂按CNY）|','|---|---|---|','|午餐|80–100/人 × 2人|160–200|','|写真|300/整组 × 1组；per_group 映射 per_package|300|','|四段交通|15–25/车/段 × 1车 × 4段；per_vehicle 映射 per_car|60–100|','|已知项目小计||520–600|','|机动金|低端按10%，高端按20%|52–120|','|含机动金的已知费用范围||572–720|','','只改通勤时长，未给车费变化，因此重算后车费仍为60–100，不能按乘客人数再乘一次。完整预算为上述范围加未知房费/附加费；未知价格没有按零计。用房可用不证明免费或已支付；写真预约不证明已支付。已付总额和实际新增支出无法分开量化，总预算上限未提供。', '', '## 修订及验收','','amend_1 将 revision 1 → 2：每段增加15分钟，四段共增加60分钟。旧交通、日程、预算汇总、意图验收及交付先标为需重算，再产出v2；原版保留为历史。复用未变化的店铺服务窗口、价格、写真预约、房间可用性和候选选择。', '', '修订后午餐后移15分钟、午休后移30分钟；出发去写真提前15分钟，16:00–17:00预约不动；回酒店由17:25改为17:40，仍在18:00前。酒店自由等候由75分钟缩到30分钟，最后余量由35分钟缩到20分钟，吸收60分钟新增交通，独立午休仍75分钟。', '', '已实际执行本地 JSON 读取、两个版本生成、时间无重叠/连续性检查、60分钟午餐及单服务窗口/点单检查、75分钟午休检查、写真预约保持检查、四段通勤时长检查、按价单位计算和预算算术检查。合成时序验收通过；现实出行核验受限。', '', '## 未知项与限制','']
lines+=['- '+u['content'] for u in unknowns]
lines+=['','没有同区天气替代候选的资料，不能编造雨天备选；如上述估计缓冲不足，应先压缩机动等候，超过可用余量则重新规划，不能自动改写真预约或取消午休。输入仅有一家指定餐厅和一家写真馆，不虚构2–4家比较。', '', '交付：delivery_bundle_v1.json 是原版历史快照；delivery_bundle_v2.json 为当前修订版；validation.json 为本次实际静态检查记录；build.py 是可复现生成与检查脚本。本次无需 Word，不执行渲染或现实地图验证。']
(O/'itinerary.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(results,ensure_ascii=False))
