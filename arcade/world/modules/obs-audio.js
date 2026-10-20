// OBS WebSocket v5: only GetInputList/GetInputMute and input meter events.
// Credentials remain in this tab's memory. No OBS settings are changed.
export async function authentication(password,salt,challenge){
 const hash=async value=>btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)))));
 return hash((await hash(password+salt))+challenge);
}
export function meterLevel(inputs,name){
 const input=inputs?.find(i=>i.inputName===name);
 const channels=input?.inputLevelsMul;
 if(!Array.isArray(channels))return 0;
 const peak=Math.max(0,...channels.map(c=>Number.isFinite(c?.[1])?Math.max(0,c[1]):0));
 return peak>0?Math.max(0,Math.min(1,(20*Math.log10(peak)+54)/54)):0;
}
export class ObsAudio{
 constructor({onLevel,onStatus,onInputs}){Object.assign(this,{onLevel,onStatus,onInputs});this.socket=null;this.source='';this.muted=true;this.last=0;this.seq=0;this.pending=new Map();}
 request(type,data={}){
  if(!this.identified||this.socket?.readyState!==1)return;
  const id=String(++this.seq);this.pending.set(id,{type,source:data.inputName});
  this.socket?.send(JSON.stringify({op:6,d:{requestType:type,requestId:id,requestData:data}}));
 }
 select(source){this.source=source;this.muted=true;this.onLevel(0);this.onStatus(source?'OBS source selected: '+source:'OBS connected — choose music source');if(source)this.request('GetInputMute',{inputName:source});}
 connect(port,password){
  this.disconnect();this.onStatus('Connecting to OBS…');
  const socket=this.socket=new WebSocket('ws://127.0.0.1:'+port);
  socket.onmessage=async event=>{
   if(this.socket!==socket)return;
   try{
    const {op,d}=JSON.parse(event.data);
    if(op===0){const identify={rpcVersion:1,eventSubscriptions:65536|8};if(d.authentication)identify.authentication=await authentication(password,d.authentication.salt,d.authentication.challenge);password='';if(this.socket===socket&&socket.readyState===1)socket.send(JSON.stringify({op:1,d:identify}));}
    if(op===2){this.identified=true;this.onStatus('OBS connected — choose music source');this.request('GetInputList');}
    if(op===7){
     const request=this.pending.get(d.requestId),type=request?.type;this.pending.delete(d.requestId);
     if(!d.requestStatus?.result){this.onStatus('OBS request failed: '+type);return;}
     if(type==='GetInputList')this.onInputs(d.responseData.inputs||[]);
     if(type==='GetInputMute'&&request.source===this.source&&d.responseData){this.muted=!!d.responseData.inputMuted;}
    }
    if(op===5&&d.eventType==='InputMuteStateChanged'&&d.eventData.inputName===this.source){this.muted=!!d.eventData.inputMuted;if(this.muted)this.onLevel(0);}
    if(op===5&&d.eventType==='InputVolumeMeters'&&this.source){
     this.last=performance.now();const level=this.muted?0:meterLevel(d.eventData.inputs,this.source);this.onLevel(level);
    }
   }catch{this.onStatus('OBS message could not be read');}
  };
  socket.onerror=()=>this.onStatus('OBS unavailable — check WebSocket settings');
  socket.onclose=e=>{if(this.socket===socket){this.socket=null;this.onLevel(0);this.onStatus(e.code===4009?'OBS password rejected':'OBS disconnected');clearInterval(this.watchdog);}};
  this.watchdog=setInterval(()=>{if(performance.now()-this.last>800)this.onLevel(0);},300);
 }
 disconnect(){const old=this.socket;this.socket=null;this.identified=false;this.source='';this.muted=true;old?.close();clearInterval(this.watchdog);this.pending.clear();this.onLevel(0);}
}
