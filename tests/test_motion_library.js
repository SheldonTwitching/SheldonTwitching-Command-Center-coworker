const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('web/overlay.css','utf8'),editor=fs.readFileSync('web/editor.html','utf8');
const names=['fade','slide-up','slide-left','zoom','pop','slide-right','slide-down','coin-flip','vs-slam','round-stamp','pixel-wipe','scan-reveal','neon-flicker','glitch-cut','stagger-bars','rank-up','arcade-boot','paint-swipe','uppercut','dash-in','spotlight','letterbox','crt-power','combo-pulse'];
for(const name of names){assert.ok(css.includes('.enter-'+name),name+' enter');assert.ok(css.includes('.exit-'+name),name+' exit');assert.ok(editor.includes('value="'+name+'"'),name+' picker');}
assert.ok(css.includes('prefers-reduced-motion'));
console.log('24 paired widget animations, shared editor pickers and reduced-motion support verified.');
