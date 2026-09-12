/* Dependency-free, explicitly interpretive 3D noodle renderer. No geometry is asserted as canon. */
(function(){
  'use strict';
  const $=id=>document.getElementById(id),canvas=$('noodleCanvas'),shell=$('noodleView');
  if(!canvas||!shell)return;
  const ctx=canvas.getContext('2d'),pairs=[['#d7383c','#3179c6'],['#d8ad2f','#398b5a'],['#dd7833','#854e9c']];
  let yaw=-.48,pitch=.72,zoom=1,raf=0,active=false,last=null,pointers=new Map();
  const presets={top:[0,0],oblique:[-.48,.72],side:[0,Math.PI/2]};
  const rotate=p=>{const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch),x=p.x*cy-p.z*sy,z=p.x*sy+p.z*cy;return{x,y:p.y*cp-z*sp,z:p.y*sp+z*cp};};
  function point(k,t,face=0){const a=k*Math.PI*2/3,rad=.49+.6*Math.cos(t),tan=.36*Math.sin(t);return{x:Math.cos(a)*rad-Math.sin(a)*tan,y:Math.sin(a)*rad+Math.cos(a)*tan,z:.15*Math.sin(2*t+k*1.7)+face*.075};}
  function size(){const d=Math.max(1,devicePixelRatio||1),r=shell.getBoundingClientRect(),w=Math.max(1,Math.round(r.width*d)),h=Math.max(1,Math.round(r.height*d));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}return{d,w,h};}
  function project(p,S){const r=rotate(p),depth=3.4-r.z,scale=Math.min(S.w,S.h)*.34*zoom/depth*3;return{x:S.w/2+r.x*scale,y:S.h/2+r.y*scale*.92,z:r.z};}
  function segments(S){const all=[],steps=150;for(let k=0;k<3;k++)for(let i=0;i<steps;i++){const t=i/steps*Math.PI*2,n=(i+1)/steps*Math.PI*2,a=project(point(k,t),S),b=project(point(k,n),S);all.push({k,a,b,z:(a.z+b.z)/2,kind:'tube'});for(const face of [-1,1]){const c=project(point(k,t,face),S),d=project(point(k,n,face),S);all.push({k,a:c,b:d,z:(c.z+d.z)/2,kind:'rail',face});}}return all.sort((a,b)=>a.z-b.z);}
  function line(s,color,width){ctx.beginPath();ctx.moveTo(s.a.x,s.a.y);ctx.lineTo(s.b.x,s.b.y);ctx.lineCap='round';ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
  function draw(){raf=0;if(!active)return;const S=size(),g=ctx.createRadialGradient(S.w*.5,S.h*.45,0,S.w*.5,S.h*.5,Math.max(S.w,S.h)*.7);g.addColorStop(0,'#fff');g.addColorStop(1,'#dce5e8');ctx.fillStyle=g;ctx.fillRect(0,0,S.w,S.h);for(const s of segments(S)){if(s.kind==='tube'){line(s,'#233843',22*S.d);line(s,'#738690',15*S.d);line(s,'#aebbc0',7*S.d);}else line(s,pairs[s.k][s.face<0?0:1],3.4*S.d);}ctx.fillStyle='#263d48';ctx.beginPath();ctx.arc(S.w/2,S.h/2,7*S.d,0,Math.PI*2);ctx.fill();}
  function request(){if(!raf)raf=requestAnimationFrame(draw);}function start(){active=true;request();}function stop(){active=false;if(raf)cancelAnimationFrame(raf);raf=0;}
  function camera(name){if(name==='reset')name='oblique';[yaw,pitch]=presets[name]||presets.oblique;zoom=1;document.querySelectorAll('[data-camera]').forEach(b=>b.classList.toggle('active',b.dataset.camera===name));request();}
  function average(){const a=[...pointers.values()];return{x:a.reduce((n,p)=>n+p.x,0)/a.length,y:a.reduce((n,p)=>n+p.y,0)/a.length,d:a.length>1?Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y):0};}
  canvas.onpointerdown=e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});canvas.setPointerCapture(e.pointerId);last=average();};
  canvas.onpointermove=e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const p=average();if(last){yaw+=(p.x-last.x)*.008;pitch=Math.max(-Math.PI/2,Math.min(Math.PI/2,pitch+(p.y-last.y)*.008));if(p.d&&last.d)zoom=Math.max(.55,Math.min(2.2,zoom*p.d/last.d));request();}last=p;};
  for(const ev of ['pointerup','pointercancel'])canvas.addEventListener(ev,e=>{pointers.delete(e.pointerId);last=pointers.size?average():null;});
  canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.55,Math.min(2.2,zoom*(e.deltaY>0?.92:1.08)));request();},{passive:false});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.1;if(e.key==='ArrowRight')yaw+=.1;if(e.key==='ArrowUp')pitch-=.1;if(e.key==='ArrowDown')pitch+=.1;if(e.key==='+'||e.key==='=')zoom*=1.1;if(e.key==='-')zoom*=.9;request();});
  document.querySelectorAll('[data-camera]').forEach(b=>b.onclick=()=>camera(b.dataset.camera));new ResizeObserver(request).observe(shell);window.Noodle3D={start,stop,camera};
})();
