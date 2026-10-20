"""Read an owner PSD/embedded PSBs; emit evidence without rewriting the source.
Optional analysis dependency: psd-tools (not a desktop-app runtime dependency).
"""
import argparse,hashlib,io,json
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.psd.descriptor import DescriptorBlock
from PIL import Image

def inspect(source,output,assets):
    source=Path(source);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(source.read_bytes()).hexdigest();root=PSDImage.open(source)
    result={'source':{'name':source.name,'sha256':digest,'bytes':source.stat().st_size},'documents':[],'assetComparisons':[]}
    seen=set()
    def plain(v):
        if hasattr(v,'items'):return {(k.decode('ascii',errors='replace') if isinstance(k,bytes) else str(k)):plain(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)) or type(v).__name__=='List':return [plain(x) for x in v]
        if hasattr(v,'value'):return plain(v.value)
        if isinstance(v,(str,int,float,bool)) or v is None:return v
        if isinstance(v,bytes):return {'byteLength':len(v)}
        return str(v)
    def visit(doc,label,depth=0):
        record={'id':label,'size':list(doc.size),'depth':doc.depth,'colorMode':str(doc.color_mode),'layers':[]};result['documents'].append(record)
        def walk(group,prefix=''):
            for i,l in enumerate(group):
                path=f'{prefix}/{i}:{l.name}'
                entry={'path':path,'name':l.name,'kind':l.kind,'bounds':list(l.bbox),'visible':l.visible,'opacity':l.opacity,'blendMode':str(l.blend_mode),'mask':l.has_mask(),'effects':[{'type':type(e).__name__,'enabled':getattr(e,'enabled',None)} for e in l.effects] if l.has_effects() else []}
                if l.has_mask():entry['maskBounds']=list(l.mask.bbox)
                metadata=l.tagged_blocks.get_data(b'shmd') or []
                animation=next((m.data for m in metadata if m.key==b'mlst'),None)
                if animation is not None:entry['frameStates']=plain(animation)
                record['layers'].append(entry)
                if l.is_group():walk(l,path)
                elif l.kind=='smartobject':
                    ob=l.smart_object;entry['smartObject']={'name':ob.filename,'kind':ob.kind,'fileType':ob.filetype,'bytes':ob.filesize}
                    if ob.kind=='data' and depth<8:
                        data=ob.data;h=hashlib.sha256(data).hexdigest();entry['smartObject']['sha256']=h
                        if data[:4]==b'8BPS' and h not in seen:
                            seen.add(h);visit(PSDImage.open(io.BytesIO(data)),label+path,depth+1)
                if label=='root' and not l.is_group() and l.kind=='pixel':
                    target=Path(assets)/(l.name+'.png')
                    if target.is_file():
                        a=l.topil().convert('RGBA');b=Image.open(target).convert('RGBA');w=min(a.width,b.width);h=min(a.height,b.height)
                        result['assetComparisons'].append({'layer':path,'asset':target.name,'sourceSize':list(a.size),'assetSize':list(b.size),'sameRGBA':a.size==b.size and a.tobytes()==b.tobytes(),'sameTopLeftOverlap':a.crop((0,0,w,h)).tobytes()==b.crop((0,0,w,h)).tobytes()})
        walk(doc)
    visit(root,'root')
    raw=root.image_resources.get_data(4003)
    if isinstance(raw,bytes) and b'AnDs' in raw:
        result['animation']=plain(DescriptorBlock.frombytes(raw[raw.index(b'AnDs')+8:]))
    if 'animation' in result:
        ids=result['animation']['FSts'][0]['FsFr'];current=result['animation']['FSts'][0]['AFrm']
        rows=[{'index':i,'id':fid,'ball':[],'arrows':[]} for i,fid in enumerate(ids)];checks=[]
        for layer in result['documents'][0]['layers']:
            states=layer.get('frameStates',{}).get('LaSt',[])
            if not states:continue
            enabled=True;lookup={}
            for state in states:
                enabled=state.get('enab',enabled)
                for fid in state.get('FrLs',[]):lookup[fid]=enabled
            if ids[current] in lookup:checks.append(lookup[ids[current]]==layer['visible'])
            for row in rows:
                if lookup.get(row['id'],False):
                    if layer['path'].startswith('/3:BALL/'):row['ball'].append(layer['name'])
                    if layer['path'].startswith('/2:ARROWS/'):row['arrows'].append(layer['name'])
        result['decodedAnimation']={'frames':rows,'selectedFrameIndex':current,'selectedFrameMatchesSavedVisibility':all(checks),'interpretation':'Visibility state deltas; omitted initial enable assumed true and checked against the selected frame.','timing':'No per-frame delay field in recovered FrIn; do not infer fps from FrGA.'}
    result['globalLightDefaults']={'angle':root.image_resources.get_data(1037),'altitude':root.image_resources.get_data(1049),'caution':'Document defaults, not evidence of the baked sphere lighting direction.'}
    # Preserve the Photoshop-saved merged preview rather than approximating its effects.
    root.topil().save(output/'original-merged-preview.png')
    root[1][0].topil().save(output/'cabinet-layer.png')
    root[1][2][1].topil().save(output/'logo-light-raw.png')
    embedded=PSDImage.open(io.BytesIO(root[1][2][0].smart_object.data));embedded.topil().save(output/'original-logo-smart-object-preview.png')
    result['sourceUnchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==digest
    assert result['sourceUnchanged'],'Source changed during read-only inspection'
    (output/'inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('--out',required=True);parser.add_argument('--assets',default='arcade/assets');a=parser.parse_args()
    r=inspect(a.source,a.out,a.assets);print(json.dumps({'documents':len(r['documents']),'layers':sum(len(d['layers']) for d in r['documents']),'identicalSprites':sum(v['sameRGBA'] for v in r['assetComparisons']),'sourceUnchanged':r['sourceUnchanged']}))
