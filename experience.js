/**
 * ΠRIME's original presentation layer. No source translation happens here.
 * Python supplies mappings and verification results through prime:visual-state.
 * The sculpture uses 3D rotation + perspective, drawn with Canvas 2D.
 */
const canvas = document.getElementById('language-sculpture');
const ctx = canvas.getContext('2d');
const host = document.getElementById('hero-visual');
const motion = document.getElementById('motion-toggle');
const preference = matchMedia('(prefers-reduced-motion: reduce)');
let paused = preference.matches, motionChosen = false, visible = true;
let width = 1, height = 1, phase = 0, targetPhase = 0, time = 0, previous = 0, frame = 0;
let pointer = {x: 0, y: 0}, viewPointer = {x: 0, y: 0};
let live = {mapping: [], units: 0, verified: false, failed: false, ready: false};
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const mix = (a, b, t) => a + (b-a)*t;
const random = index => {const value = Math.sin(index*127.1+53.7)*43758.5453;return value-Math.floor(value);};
const piOutline = [[-1.8,1.7],[1.8,1.7],[1.8,1.05],[1.25,1.05],[1.25,-1.7],[.55,-1.7],[.55,1.05],[-.55,1.05],[-.55,-1.7],[-1.25,-1.7],[-1.25,1.05],[-1.8,1.05]];
const cubeVertices = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
const cubeFaces = [[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[1,2,6,5],[0,4,7,3]];

// Rotation about X and Y, followed by perspective projection onto the canvas.
function rotate(point, rx, ry, rz=0) {
  let [x,y,z] = point;
  [y,z] = [y*Math.cos(rx)-z*Math.sin(rx),y*Math.sin(rx)+z*Math.cos(rx)];
  [x,z] = [x*Math.cos(ry)+z*Math.sin(ry),-x*Math.sin(ry)+z*Math.cos(ry)];
  return [x*Math.cos(rz)-y*Math.sin(rz),x*Math.sin(rz)+y*Math.cos(rz),z];
}
function project(point) {
  const depth = 8/(8+point[2]);
  const scale = Math.min(width*.15,height*.19);
  return {x:width*.52+point[0]*depth*scale,y:height*.48-point[1]*depth*scale,z:point[2]};
}
function path(points) {
  ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();
}
function paintFace(points, opacity, accent=false, front=false) {
  const xs=points.map(p=>p.x),ys=points.map(p=>p.y);
  const x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x,h=Math.max(...ys)-y;
  const gradient=ctx.createLinearGradient(x,y,x+Math.max(w,1),y+Math.max(h,1));
  const stops=accent?['#d6efbc','#53795d','#172c29','#c6e9ac','#345b50','#eff6dc']:['#e8ede5','#69777b','#151d24','#bcc7c8','#3b4651','#e2e8de'];
  stops.forEach((color,i)=>gradient.addColorStop(i/(stops.length-1),color));
  ctx.save();ctx.globalAlpha=opacity;path(points);ctx.fillStyle=gradient;ctx.fill();
  ctx.strokeStyle=accent?'rgba(224,255,178,.7)':'rgba(224,238,240,.42)';ctx.lineWidth=front?1.1:.65;ctx.stroke();
  if(front){ctx.clip();const shine=ctx.createLinearGradient(x,y,x+w,y+h);shine.addColorStop(0,'#ffffff00');shine.addColorStop(.39,'#ffffff00');shine.addColorStop(.46,'#ffffff80');shine.addColorStop(.53,'#ffffff00');shine.addColorStop(1,'#ffffff00');ctx.fillStyle=shine;ctx.fillRect(x,y,w,h);}
  ctx.restore();
}
function piFaces(rx,ry,rz) {
  const front=piOutline.map(([x,y])=>project(rotate([x,y,.36],rx,ry,rz)));
  const back=piOutline.map(([x,y])=>project(rotate([x,y,-.36],rx,ry,rz)));
  const faces=[{points:front,front:true},{points:back,front:false}];
  for(let i=0;i<front.length;i++){const j=(i+1)%front.length;faces.push({points:[front[i],front[j],back[j],back[i]],front:false});}
  return faces.sort((a,b)=>b.points.reduce((n,p)=>n+p.z,0)/b.points.length-a.points.reduce((n,p)=>n+p.z,0)/a.points.length);
}
function paintCube(position,index,amount,rx,ry) {
  const size=.11+random(index+7)*.08;
  const vertices=cubeVertices.map(v=>project(rotate(v.map((n,j)=>n*size+position[j]),rx,ry)));
  const faces=cubeFaces.map(indices=>indices.map(i=>vertices[i])).sort((a,b)=>b.reduce((n,p)=>n+p.z,0)-a.reduce((n,p)=>n+p.z,0));
  faces.forEach((face,i)=>paintFace(face,amount*(.45+i*.09),index%5===0));
}
function paintOrbit(rx,ry,amount) {
  ctx.save();ctx.globalAlpha=amount;ctx.strokeStyle='#b9d1c755';ctx.lineWidth=.75;ctx.beginPath();
  for(let i=0;i<=100;i++){const angle=i/100*Math.PI*2;const p=project(rotate([Math.cos(angle)*2.5,-1.95,Math.sin(angle)*1.35],rx,ry));i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}
  ctx.stroke();ctx.restore();
}
function paintTokens(rx,ry,burst) {
  const pairs=live.mapping.slice(0,8);
  pairs.forEach(([unit,alias],i)=>{
    const angle=i/pairs.length*Math.PI*2+time*.035;
    const p=project(rotate([Math.cos(angle)*(2.35+burst*.35),Math.sin(angle)*1.9,Math.sin(angle*2)*.8],rx*.25,ry*.35));
    const token=targetPhase===1?alias:unit.slice(unit.indexOf(':')+1);
    const label=token.length>12?token.slice(0,11)+'…':token;
    ctx.font='13px ui-monospace,Consolas,monospace';const w=Math.max(40,ctx.measureText(label).width+24);
    ctx.fillStyle='rgba(18,25,28,.85)';ctx.strokeStyle=targetPhase===1?'#ccebaa66':'#8c9a9f55';ctx.lineWidth=.6;
    ctx.beginPath();ctx.roundRect(p.x-w/2,p.y-15,w,30,5);ctx.fill();ctx.stroke();
    ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=targetPhase===1?'#d8f4ac':'#cbd4d5';ctx.fillText(label,p.x,p.y);
  });
}
function paintScene() {
  ctx.clearRect(0,0,width,height);
  const glow=ctx.createRadialGradient(width*.53,height*.5,0,width*.53,height*.5,width*.5);
  glow.addColorStop(0,'#bacf9b0d');glow.addColorStop(.48,'#94adc508');glow.addColorStop(1,'#080b0d00');ctx.fillStyle=glow;ctx.fillRect(0,0,width,height);
  for(let i=0;i<100;i++){
    const x=random(i+11)*width,y=(random(i+501)*height-time*(2+random(i)*3)+height*10)%height;
    ctx.fillStyle=i%7===0?'#d4edb944':'#b9ced933';ctx.beginPath();ctx.arc(x,y,i%9===0?1.2:.55,0,Math.PI*2);ctx.fill();
  }
  const rx=-.12+viewPointer.y*.16,ry=-.42+viewPointer.x*.3+Math.sin(time*.17)*.08,rz=-.07+Math.sin(time*.22)*.015;
  const burst=Math.sin(phase*Math.PI/2),solid=1-burst*.88;
  const shadow=ctx.createRadialGradient(width*.52,height*.83,0,width*.52,height*.83,width*.3);
  shadow.addColorStop(0,'#000000a0');shadow.addColorStop(1,'#00000000');ctx.fillStyle=shadow;ctx.fillRect(0,height*.6,width,height*.4);
  paintOrbit(rx,ry,.55+burst*.25);
  const fragments=Array.from({length:24},(_,i)=>{
    const angle=i*2.39996+time*.06;
    return {position:[Math.cos(angle)*(1.6+random(i+31)*1.5),Math.sin(angle)*(1.35+random(i+70)),(random(i+90)-.5)*2.7],index:i};
  });
  fragments.sort((a,b)=>b.position[2]-a.position[2]);
  fragments.filter(x=>x.position[2]<0).forEach(x=>paintCube(x.position,x.index,burst*.8,rx,ry));
  piFaces(rx,ry,rz).forEach(face=>paintFace(face.points,solid*(face.front?1:.72),live.verified&&targetPhase===2,face.front));
  fragments.filter(x=>x.position[2]>=0).forEach(x=>paintCube(x.position,x.index,burst*.9,rx,ry));
  paintTokens(rx,ry,burst);
  if(live.mapping.length){
    const [unit,alias]=live.mapping[Math.floor(time*.18)%live.mapping.length];
    document.getElementById('scene-token').textContent=unit.slice(unit.indexOf(':')+1)+'  /  '+alias;
    document.getElementById('scene-token-label').textContent=live.dirty?'Apply pending definition edits':'Live pair from the active Python definition';
  }
}
function animate(timestamp) {
  frame=0;if(!visible||document.hidden)return;
  const elapsed=Math.min((timestamp-previous)/1000,.05);if(!paused&&timestamp-previous<32){schedule();return;}previous=timestamp;
  if(!paused)time+=elapsed;
  phase=paused?targetPhase:mix(phase,targetPhase,.065);
  if(!paused){viewPointer.x=mix(viewPointer.x,pointer.x,.06);viewPointer.y=mix(viewPointer.y,pointer.y,.06);}
  paintScene();if(!paused)schedule();
}
function schedule(){if(!frame)frame=requestAnimationFrame(animate);}
function resize(){const rect=host.getBoundingClientRect();width=rect.width;height=rect.height;const ratio=Math.min(devicePixelRatio||1,1.7);canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);schedule();}
function updateMotion(){motion.textContent=paused?'Play motion':'Pause motion';motion.setAttribute('aria-pressed',String(paused));schedule();}
motion.addEventListener('click',()=>{motionChosen=true;paused=!paused;updateMotion();});
preference.addEventListener('change',event=>{if(!motionChosen){paused=event.matches;updateMotion();}});
host.addEventListener('pointermove',event=>{const rect=host.getBoundingClientRect();pointer={x:clamp((event.clientX-rect.left)/rect.width*2-1,-1,1),y:clamp((event.clientY-rect.top)/rect.height*2-1,-1,1)};schedule();});
host.addEventListener('pointerleave',()=>{pointer={x:0,y:0};schedule();});
new ResizeObserver(resize).observe(host);
new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)schedule();},{threshold:.01}).observe(host);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)schedule();});

function selectPhase(value){
  targetPhase=value;
  document.querySelectorAll('[data-scene-mode]').forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.sceneMode)===value)));
  document.getElementById('scene-state').textContent=['SOURCE / STRUCTURE','LANGUAGE / REPRESENTATION',live.verified?'RECOVERY / EXACT MATCH':'RECOVERY / PYTHON CHECK'][value];
  schedule();
}
document.querySelectorAll('[data-scene-mode]').forEach(button=>button.addEventListener('click',()=>selectPhase(Number(button.dataset.sceneMode))));
document.addEventListener('prime:visual-state',event=>{
  live=event.detail;
  document.getElementById('hero-token-count').textContent=live.units||'—';
  document.getElementById('hero-verification').textContent=live.verified?'Exact source + AST match':live.failed?'Current document differs':'Run the Python check';
  const map=document.getElementById('process-mapping');map.replaceChildren();
  for(const [unit,alias] of live.mapping.slice(0,4)){
    const row=document.createElement('div'),source=document.createElement('code'),target=document.createElement('code');
    source.textContent=unit.slice(unit.indexOf(':')+1);target.textContent=alias;row.append(source,target);map.append(row);
  }
  selectPhase(targetPhase);schedule();
});

// Scroll changes the explanatory layer emphasis, never source or its rules.
const graphic=document.querySelector('.process-graphic');
const steps=[...document.querySelectorAll('[data-process-stage]')];
let scrollFrame=0;
function updateProcess(){
  scrollFrame=0;
  const centre=innerHeight*.52;
  const active=steps.reduce((best,step)=>Math.abs(step.getBoundingClientRect().top+step.offsetHeight*.5-centre)<Math.abs(best.getBoundingClientRect().top+best.offsetHeight*.5-centre)?step:best,steps[0]);
  const stage=Number(active.dataset.processStage);graphic.dataset.stage=String(stage);
  steps.forEach(step=>step.classList.toggle('active',step===active));
  document.getElementById('process-stage-caption').textContent=['Source tokens, preserved with their original layout.','Explicit aliases from your active Python definition.','Restore the framed representation with its matching definition.'][stage];
}
addEventListener('scroll',()=>{if(!scrollFrame)scrollFrame=requestAnimationFrame(updateProcess);},{passive:true});
addEventListener('resize',updateProcess);
const reveal=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in-view');reveal.unobserve(entry.target);}}),{threshold:.12});
document.querySelectorAll('.section-intro,.mode-card,.about-columns').forEach(element=>{element.classList.add('reveal-ready');reveal.observe(element);});
updateProcess();updateMotion();
