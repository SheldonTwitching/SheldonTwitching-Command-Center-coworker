'use strict';
/* Configure just the labels below for your own stream. OBS Browser Source may load these as local HTML files. */
const scenes = {
  gameplay: { title: '', subtitle: '', footnote: '' },
  starting: { title: 'STARTING SOON', subtitle: 'INSERT COIN  ·  GET READY', footnote: 'The next set is about to begin!' },
  brb: { title: 'BE RIGHT BACK', subtitle: 'PLAYER 1 CONTINUES', footnote: 'Quick break — back in a moment!' },
  ending: { title: 'GAME OVER', subtitle: 'THANKS FOR PLAYING', footnote: 'See you at the next cabinet!' }
};
function initScene(){
 const basename=(location.pathname.split('/').pop()||'').split('.')[0].toLowerCase();
 const override=(new URLSearchParams(location.search)).get('scene');
 const view=Object.hasOwn(scenes,override)?override:(Object.hasOwn(scenes,basename)?basename:'gameplay');
 const stage=document.querySelector('#stage');stage.dataset.scene=view;
 document.querySelector('#main-title').textContent=scenes[view].title;
 document.querySelector('#subtitle').textContent=scenes[view].subtitle;
 document.querySelector('#footnote').textContent=scenes[view].footnote;
 document.title=`SheldonTwitching ${view.toUpperCase()} scene`;
 function resize(){const scale=Math.min(innerWidth/1920,innerHeight/1080);stage.style.setProperty('--scale',scale);stage.style.left=`${Math.max(0,(innerWidth-1920*scale)/2)}px`;stage.style.top=`${Math.max(0,(innerHeight-1080*scale)/2)}px`}
 addEventListener('resize',resize);resize();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initScene);else initScene();