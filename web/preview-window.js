import {openPreview} from './preview-popout.js';
const $=id=>document.getElementById(id),q=new URLSearchParams(location.search);let source;
try{source=new URL(q.get('source')||'/studio/scene',location.origin);if(source.origin!==location.origin||source.pathname==='/preview-window')throw Error('Choose a local preview source.');}catch(e){$('source').textContent=e.message;throw e;}
const editor=q.get('mode')==='editor';document.body.classList.toggle('editor',editor);$('title').textContent=editor?'EDITOR WINDOW':'LIVE PREVIEW';$('output').src=source.href;$('clean').href=source.href;$('source').textContent=source.pathname+source.search;
const edit=new URL(q.get('editor')||'/studio',location.origin);$('editor').href=edit.origin===location.origin?edit.href:'/studio';$('editor').onclick=e=>{e.preventDefault();openPreview($('editor').href,'/studio',true);};
let width=1920,height=1080,scale=1,fitting=true;
if(source.pathname==='/arcade/overlay'||source.searchParams.get('view')==='native'){width=2060;height=1220;}
if(source.searchParams.get('format')==='vertical'){width=1080;height=1920;}
try{const spec=await(await fetch('/arcade/project-spec.json')).json(),entry=spec.sources.find(s=>s.url===source.pathname+source.search||s.url===source.pathname);if(entry&&!source.searchParams.has('view')&&!source.searchParams.has('format')){width=entry.width;height=entry.height;}
 if(source.pathname==='/overlay'){const p=await(await fetch('/api/project')).json();width=p.width;height=p.height;}
}catch{}
function size(){if(editor)return;const view=$('viewport');if(fitting)scale=Math.min(view.clientWidth/width,view.clientHeight/height);$('output').style.width=width+'px';$('output').style.height=height+'px';$('output').style.transform='scale('+scale+')';$('extent').style.width=width*scale+'px';$('extent').style.height=height*scale+'px';$('percent').textContent=Math.round(scale*100)+'%';$('zoom').value=Math.round(scale*100);}
$('fit').onclick=()=>{fitting=true;size();};$('native').onclick=()=>{fitting=false;scale=1;size();};$('zoom').oninput=()=>{fitting=false;scale=Number($('zoom').value)/100;size();};$('reload').onclick=()=>$('output').src=source.href;$('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();$('background').onchange=()=>{const v=$('background').value;$('viewport').style.backgroundImage=v==='checker'?'':'none';$('viewport').style.backgroundColor=v==='checker'?'#151322':v;};
function layout(){ $('viewport').style.top=($('viewport').previousElementSibling.getBoundingClientRect().bottom+8)+'px';size();}new ResizeObserver(layout).observe(document.querySelector('header'));addEventListener('resize',layout);layout();
if(editor){for(const id of ['fit','native','zoom','percent'])$(id).hidden=true;}
