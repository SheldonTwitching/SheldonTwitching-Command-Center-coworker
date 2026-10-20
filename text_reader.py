"""Bounded local text feeds, independent of the rotating Streamlabels project."""
import math
import re
from pathlib import Path

MODES=('raw','lines','words','characters','occurrences','sum','before','after')

def validate_reader(value):
    if not isinstance(value,dict) or set(value)!={'path','mode','needle','fallback'}:
        raise ValueError('Invalid text reader')
    if value['mode'] not in MODES:raise ValueError('Unknown text operation')
    for key,limit in [('path',4096),('needle',200),('fallback',500)]:
        if not isinstance(value[key],str) or len(value[key])>limit:raise ValueError('Invalid text '+key)
    if value['path'] and Path(value['path']).suffix.lower()!='.txt':raise ValueError('Choose a .txt file')
    return value

def read_text(value):
    validate_reader(value)
    if not value['path']:return {'connected':False,'value':value['fallback'],'error':'Choose a text file'}
    try:
        with Path(value['path']).open('rb') as stream:raw=stream.read(65537)
        if len(raw)>65536:raise ValueError('Text file exceeds 64 KB')
        try:text=raw.decode('utf-8-sig')
        except UnicodeDecodeError:text=raw.decode('cp1252')
        mode=value['mode'];needle=value['needle']
        if mode=='lines':result=str(len([line for line in text.splitlines() if line.strip()]))
        elif mode=='words':result=str(len(text.split()))
        elif mode=='characters':result=str(len(text))
        elif mode=='occurrences':result=str(text.count(needle)) if needle else '0'
        elif mode=='sum':
            total=sum(float(n.replace(',','')) for n in re.findall(r'-?\d[\d,]*(?:\.\d+)?',text))
            if not math.isfinite(total):raise ValueError('Numeric total is too large')
            result=f'{total:g}'
        elif mode in ('before','after'):
            parts=text.partition(needle) if needle else (text,'','')
            result=(parts[0] if mode=='before' else parts[2]) if parts[1] else value['fallback']
        else:result=text
        return {'connected':True,'value':result,'bytes':len(raw),'mode':mode}
    except (OSError,ValueError) as error:
        return {'connected':False,'value':value['fallback'],'error':str(error)}
