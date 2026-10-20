// Project independent canvases into their cabinet screens using a homography.
export function surface(width,height,points){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;canvas.className='surface';
  const src=[[0,0],[width,0],[width,height],[0,height]], rows=[];
  src.forEach(([x,y],i)=>{const [u,v]=points[i];rows.push([x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]);});
  for(let col=0;col<8;col++){let pivot=col;for(let j=col+1;j<8;j++)if(Math.abs(rows[j][col])>Math.abs(rows[pivot][col]))pivot=j;[rows[col],rows[pivot]]=[rows[pivot],rows[col]];let p=rows[col][col];for(let k=col;k<9;k++)rows[col][k]/=p;for(let j=0;j<8;j++)if(j!==col){let a=rows[j][col];for(let k=col;k<9;k++)rows[j][k]-=a*rows[col][k];}}
  const [a,b,c,d,e,f,g,h]=rows.map(r=>r[8]);canvas.style.transform=`matrix3d(${a},${d},0,${g},${b},${e},0,${h},0,0,1,0,${c},${f},0,1)`;
  document.querySelector('#surfaces').append(canvas);const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;return ctx;
}
export function text(ctx,str,x,y,size=14,color='#e9e2ff',align='left'){ctx.fillStyle=color;ctx.font=`bold ${size}px monospace`;ctx.textAlign=align;ctx.fillText(str,x,y);}
export function timecode(seconds){return `${Math.floor(seconds/60).toString().padStart(2,'0')}:${(seconds%60).toString().padStart(2,'0')}`;}
