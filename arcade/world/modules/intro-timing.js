export const INTRO_DURATION=7;
export const STINGER_DURATION=1.7;
export function introSample(elapsed,stingerOnly=false){
 const t=Math.max(0,elapsed)+(stingerOnly?5.3:0);
 if(t<.8)return {phase:'boot',progress:t/.8,coverage:0};
 if(t<4.6)return {phase:'logo',progress:Math.min(1,(t-.8)/.45),coverage:0};
 if(t<5.3)return {phase:'charge',progress:(t-4.6)/.7,coverage:0};
 if(t<6)return {phase:'wipe-in',progress:(t-5.3)/.7,coverage:(t-5.3)/.7};
 if(t<6.2)return {phase:'cut',progress:1,coverage:1};
 if(t<7)return {phase:'wipe-out',progress:(t-6.2)/.8,coverage:1-(t-6.2)/.8};
 return {phase:'complete',progress:1,coverage:0};
}
