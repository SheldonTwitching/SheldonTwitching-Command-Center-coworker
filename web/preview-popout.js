// Editor-only pop-outs. Never loaded into clean OBS sources.
export function openPreview(source,editor=location.pathname,editorMode=false){
 const target=new URL(source,location.origin);if(target.origin!==location.origin)return;
 const url='/preview-window?'+new URLSearchParams({source:target.pathname+target.search+target.hash,editor,mode:editorMode?'editor':'preview'});
 const api=window.pywebview?.api||window.parent?.pywebview?.api||window.top?.pywebview?.api;
 if(api?.open_preview)api.open_preview(url).then(result=>{if(!result?.ok)alert(result?.error||'Could not open preview');}).catch(()=>alert('Could not open the preview window.'));
 else if(!window.open(url,'_blank','popup=yes,resizable=yes,scrollbars=yes,width=1200,height=850'))alert('Allow pop-ups for this local app to open a separate preview.');
}
function button(label,action){const b=document.createElement('button');b.type='button';b.textContent=label;b.className='btn subtle preview-popout';b.onclick=action;return b;}
for(const frame of document.querySelectorAll('iframe#scene-preview,iframe#preview,iframe#tool-frame')){
 const editorMode=frame.id==='tool-frame',b=button(editorMode?'Pop out editor':'Pop out preview',()=>openPreview(frame.getAttribute('src')||'/studio',location.pathname,editorMode));
 b.setAttribute('aria-label',editorMode?'Pop out active editor':'Pop out '+(frame.title||'preview'));
 const toolbar=frame.id==='scene-preview'?document.querySelector('#preview-column .preview-toolbar'):frame.id==='preview'?document.querySelector('.view-head,.row:has(#clean)'):null;
 if(toolbar)toolbar.append(b);else frame.before(b);
 const sync=()=>{b.hidden=frame.hidden||!frame.getAttribute('src');};new MutationObserver(sync).observe(frame,{attributes:true,attributeFilter:['hidden','src']});sync();
}
if(document.getElementById('previewHost'))document.querySelector('.preview-actions').append(button('Pop out label preview',()=>openPreview('/overlay','/editor')));
// The source catalog is populated asynchronously and includes every individual widget/part.
const catalog=document.getElementById('source-links');if(catalog){const add=()=>{for(const card of catalog.querySelectorAll('article'))if(!card.querySelector('.preview-popout')){const a=card.querySelector('a');if(a)card.append(button('Pop out preview',()=>openPreview(a.href,location.pathname)));}};new MutationObserver(add).observe(catalog,{childList:true,subtree:true});add();}
