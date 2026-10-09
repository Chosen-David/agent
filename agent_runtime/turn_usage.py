"""Single current no-tool turn accounting on fresh or inherited threads."""
def current_turn_usage(events,thread_id,turn_id):
    starts=[];ends=[];snapshots=[];done=False
    allowed={'userMessage','agentMessage','reasoning'}
    for e in events:
        if not isinstance(e,dict):raise ValueError('invalid native event')
        method=e.get('method','');p=e.get('params',{})
        if method=='error':raise ValueError('native error during measured turn')
        if p.get('threadId')!=thread_id:continue
        if method in ('turn/started','turn/completed'):
            t=p.get('turn',{})
            if t.get('id')!=turn_id or done:raise ValueError('wrong or duplicate terminal turn')
            if method=='turn/started':starts.append(t)
            else:
                if not starts or t.get('status')!='completed' or t.get('error') or any(x.get('type') not in allowed for x in t.get('items',[])):
                    raise ValueError('failed or nontrivial measured turn')
                ends.append(t);done=True
        elif method=='thread/tokenUsage/updated' or method in ('item/started','item/completed'):
            if not starts or done or p.get('turnId')!=turn_id:raise ValueError('item/usage outside current turn')
            if method=='thread/tokenUsage/updated':snapshots.append(p.get('tokenUsage',{}))
            elif p.get('item',{}).get('type') not in allowed:raise ValueError('measured turn used tools')
    if len(starts)!=1 or len(ends)!=1 or not snapshots:raise ValueError('one successful observed turn required')
    last=snapshots[-1].get('last',{});total=snapshots[-1].get('total',{})
    fields=('inputTokens','cachedInputTokens','outputTokens','totalTokens','reasoningOutputTokens')
    for u in (last,total):
        if any(type(u.get(k)) is not int or u[k]<0 for k in fields):raise ValueError('missing/inconsistent native counters')
        if u['totalTokens']!=u['inputTokens']+u['outputTokens'] or u['cachedInputTokens']>u['inputTokens'] or u['reasoningOutputTokens']>u['outputTokens']:
            raise ValueError('inconsistent native counter arithmetic')
    if any(total[k]<last[k] for k in fields):raise ValueError('cumulative usage smaller than current turn')
    return {'thread_id':thread_id,'turn_id':turn_id,'input_tokens':last['inputTokens'],'cached_input_tokens':last['cachedInputTokens'],
        'output_tokens':last['outputTokens'],'total_tokens':last['totalTokens'],'reasoning_output_tokens':last['reasoningOutputTokens'],
        'source':'native final current-turn tokenUsage.last; never cumulative summation or subtraction',
        'scope':'this one no-tool turn, including all history charged as current input; already paid parent actions excluded; cache not subtracted'}
