import {nameplate,nameplateReady} from './nameplate.js?v=18';
// Styling preview only. No fabricated live labels, Spotify or donations.
export function createWidgetLayout(stage){
 const dock=document.createElement('section');dock.id='widget-layout';dock.setAttribute('aria-label','Sample graffiti widget layout');
 dock.innerHTML='<span class="sample-label">LAYOUT PREVIEW · SAMPLE CONTENT</span><article class="widget-sample support"><canvas aria-hidden="true"></canvas><span class="widget-icon">ST</span><div><small class="support-label">LATEST FOLLOWER</small><strong class="support-value">Follower name</strong></div></article><article class="widget-sample goal"><canvas aria-hidden="true"></canvas><span class="widget-icon">ST</span><div><small>STREAM COSTS</small><strong>Goal title <em>40% · sample</em></strong><span class="goal-track"><i></i></span></div></article><article class="widget-sample playing"><canvas aria-hidden="true"></canvas><span class="widget-icon music-icon">♫</span><div><small>NOW PLAYING</small><strong>Track title</strong><span class="artist">Artist name</span></div></article>';
 stage.append(dock);
 const cards=[...dock.querySelectorAll('article')];
 function paint(){for(const card of cards){if(!card.clientWidth||!card.clientHeight)continue;const c=card.querySelector('canvas');c.width=Math.round(card.clientWidth);c.height=card.clientHeight;nameplate(c.getContext('2d'),0,0,c.width,c.height,card.classList.contains('playing')?'#43b5f0':'#9664ed');}}
 const observer=new ResizeObserver(paint);cards.forEach(card=>observer.observe(card));
 paint();nameplateReady.then(paint);let loads=0;const artTimer=setInterval(()=>{paint();if(++loads>10)clearInterval(artTimer);},700);
 let donor=false;const timer=setInterval(()=>{donor=!donor;const card=dock.querySelector('.support');card.classList.remove('label-change');void card.offsetWidth;card.classList.add('label-change');dock.querySelector('.support-label').textContent=donor?'LATEST DONOR':'LATEST FOLLOWER';dock.querySelector('.support-value').textContent=donor?'Donor name':'Follower name';},7000);
 addEventListener('pagehide',()=>{clearInterval(timer);clearInterval(artTimer);observer.disconnect();},{once:true});
 return dock;
}
