import {text,timecode} from './surface.js?v=18';
import {nameplate} from './nameplate.js?v=18';
export function drawCountdown(ctx,s,p,brb=false){
 ctx.fillStyle='#10081c';ctx.fillRect(0,0,500,110);
 // Typography belongs to the cabinet's actual illuminated marquee, not a UI box.
 text(ctx,brb?'BE RIGHT BACK':'STARTING SOON',24,33,22,p.color);
 text(ctx,'ST',25,87,43,p.accent);
 text(ctx,brb?'ARCADE OPEN':s.remaining?'LIVE IN':'SHOW READY',476,32,16,p.accent,'right');
 text(ctx,brb?'BRB':timecode(s.remaining),476,89,55,'#fff','right');
}
export function drawLowerThird(ctx,s,p,brb=false){
 nameplate(ctx,40,747,913,68,'#80d7ff');
 text(ctx,'ST',62,790,27,'#80d7ff');text(ctx,brb?'BE RIGHT BACK':'STARTING SOON',125,787,27,'#fff');
 text(ctx,brb?'CHAT CLASH CONTINUES':timecode(s.remaining),926,790,33,'#80d7ff','right');
}
