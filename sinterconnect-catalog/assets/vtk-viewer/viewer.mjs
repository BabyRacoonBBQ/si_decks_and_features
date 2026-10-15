import '@kitware/vtk.js/Rendering/Profiles/Geometry.js';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow.js';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor.js';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper.js';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData.js';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray.js';
import vtkColorTransferFunction from '@kitware/vtk.js/Rendering/Core/ColorTransferFunction.js';
import vtkAnnotatedCubeActor from '@kitware/vtk.js/Rendering/Core/AnnotatedCubeActor.js';
import vtkOrientationMarkerWidget from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget.js';
import { Corners } from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget/Constants.js';

const EDGES = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
const PALETTE = [[0, .19,.16,.48], [.25,.13,.48,.72], [.5,.12,.72,.65], [.75,.96,.78,.24], [1,.72,.12,.12]];
const GRADIENT = 'linear-gradient(to right,' + PALETTE.map(([t,r,g,b]) => `rgb(${r*255} ${g*255} ${b*255}) ${t*100}%`).join(',') + ')';
const FIELDS = {
  material: {label:'Materials'}, stress:{label:'Copper von Mises stress',unit:'MPa',range:[0,750],copper:true},
  temperature:{label:'Temperature',unit:'°C'}, potential:{label:'Copper potential',unit:'V',range:[0,.1],copper:true},
};

function unpack(item) {
  const Type = {Float32Array,Uint32Array}[item.type];
  if (!Type || !Number.isSafeInteger(item.length) || item.length<0 || item.length>5000000) throw Error('Invalid model array');
  const bytes=Uint8Array.from(atob(item.data), c=>c.charCodeAt(0));
  if (bytes.byteLength!==item.length*4) throw Error('Model array length mismatch');
  return new Type(bytes.buffer);
}

function prepareRegion(region) {
  const points=unpack(region.points), tets=unpack(region.tetrahedra), polygons=unpack(region.polygons);
  if (points.length%3 || tets.length%4 || polygons.length%4) throw Error('Invalid model topology');
  const count=points.length/3;
  if (tets.some(i=>i>=count)) throw Error('Invalid tetrahedral point index');
  for(let i=0;i<polygons.length;i+=4) {
    if(polygons[i]!==3 || polygons.slice(i+1,i+4).some(j=>j>=count)) throw Error('Invalid surface point index');
  }
  const states=Object.fromEntries(Object.entries(region.states).map(([stage,fields])=>[stage,
    Object.fromEntries(Object.entries(fields).map(([name,value])=>{
      const values=unpack(value);if(values.length!==count)throw Error('Invalid nodal field');return [name,values];
    }))]));
  return {...region, points,tets,polygons,states};
}

function polyData(points, polygons) {
  const data=vtkPolyData.newInstance();
  data.getPoints().setData(points,3);data.getPolys().setData(polygons);
  return data;
}

// Intersect the actual volume tetrahedra; keep weights for nodal field sampling.
function section(region,y) {
  const vertices=[],polygons=[],samples=[],seen=new Set();
  const {points,tets}=region, eps=1e-8;
  for(let i=0;i<tets.length;i+=4) {
    const ids=[tets[i],tets[i+1],tets[i+2],tets[i+3]], d=ids.map(id=>points[id*3+1]-y);
    if(Math.min(...d)>eps || Math.max(...d)<-eps)continue;
    const hits=[], keys=new Set();
    const add=(a,b,t)=>{
      const p=[0,1,2].map(k=>points[a*3+k]+t*(points[b*3+k]-points[a*3+k]));
      p[1]=y; const key=p.map(v=>Math.round(v/eps)).join(',');
      if(!keys.has(key)){keys.add(key);hits.push({p,sample:[a,b,t],key});}
    };
    ids.forEach((id,j)=>{if(Math.abs(d[j])<=eps)add(id,id,0);});
    EDGES.forEach(([a,b])=>{if(d[a]*d[b]<0 && Math.abs(d[a])>eps && Math.abs(d[b])>eps)add(ids[a],ids[b],-d[a]/(d[b]-d[a]));});
    if(hits.length<3)continue;
    const signature=hits.map(h=>h.key).sort().join('|');
    if(seen.has(signature))continue;seen.add(signature);
    const cx=hits.reduce((s,h)=>s+h.p[0],0)/hits.length, cz=hits.reduce((s,h)=>s+h.p[2],0)/hits.length;
    hits.sort((a,b)=>Math.atan2(a.p[2]-cz,a.p[0]-cx)-Math.atan2(b.p[2]-cz,b.p[0]-cx));
    for(let j=1;j<hits.length-1;j++) {
      const start=vertices.length/3;
      for(const h of [hits[0],hits[j],hits[j+1]]){vertices.push(...h.p);samples.push(h.sample);}
      polygons.push(3,start,start+1,start+2);
    }
  }
  return {data:polyData(new Float32Array(vertices),new Uint32Array(polygons)),samples};
}

function mount(root,model) {
  if(model.schemaVersion!==1)throw Error('Unsupported model version');
  const regions=model.regions.map(prepareRegion), materials=[...new Set(regions.map(r=>r.material))];
  root.innerHTML=`<div class="vtk-toolbar">
    <label class="vtk-control">State<select data-control="stage" aria-label="Simulation state"></select></label>
    <label class="vtk-control">Color by<select data-control="field" aria-label="Color by"></select></label>
    <label class="vtk-control">View<select data-control="view" aria-label="Model view"><option value="surface">3D model</option><option value="section">Y section</option></select></label>
  </div><div class="vtk-display"><div class="vtk-materials" aria-label="Visible materials"></div>
    <button type="button" data-action="copper">Copper only</button><button type="button" data-action="stack">Show stack</button>
    <label class="vtk-check"><input type="checkbox" data-control="edges">Mesh edges</label>
    <label class="vtk-context">Context opacity<input type="range" min="0" max="1" step="0.05" value="0.15" data-control="opacity" aria-label="Context opacity"></label>
  </div><div class="vtk-viewport"><div class="vtk-canvas" tabindex="0" role="img" aria-label="Interactive three-dimensional simulation model. Drag to rotate, shift-drag to pan, scroll to zoom. Arrow keys rotate; plus and minus zoom."></div>
    <div class="vtk-overlay"><b></b><span></span></div><div class="vtk-view-buttons"><button type="button" data-action="reset">Reset view</button><button type="button" data-action="front">Front (Y)</button></div>
    <div class="vtk-legend" hidden><div class="vtk-legend-title"></div><div class="vtk-colorbar"></div><div class="vtk-range"><span></span><span></span></div></div>
  </div><div class="vtk-section-controls" hidden><label>Section position · Y (μm)</label><input type="range" data-control="section" aria-label="Section position Y in micrometers" step="0.001"><output></output></div>
  <div class="vtk-footer"><span>Drag to rotate · Shift + drag to pan · Scroll / pinch to zoom</span><span>Undeformed geometry · coordinates in μm · VTK.js</span></div>`;
  const find=selector=>root.querySelector(selector), controls=Object.fromEntries([...root.querySelectorAll('[data-control]')].map(el=>[el.dataset.control,el]));
  for(const state of model.stages)controls.stage.add(new Option(state.label,state.id));controls.stage.value='3';
  for(const [key,field] of Object.entries(FIELDS))controls.field.add(new Option(field.label+(field.unit?` (${field.unit})`:''),key));
  controls.section.min=model.sectionRange[0];controls.section.max=model.sectionRange[1];controls.section.value=model.sectionDefault;
  const checks=new Map();
  materials.forEach(material=>{
    const label=document.createElement('label'),check=document.createElement('input'),swatch=document.createElement('span');
    check.type='checkbox';check.checked=true;check.dataset.material=material;check.setAttribute('aria-label',`Show ${material}`);
    swatch.className='vtk-swatch';swatch.style.background=regions.find(r=>r.material===material).color;
    label.append(check,swatch,document.createTextNode(material));find('.vtk-materials').append(label);checks.set(material,check);
  });
  const canvas=find('.vtk-canvas');
  const context=document.createElement('canvas').getContext('webgl2');
  if(!context)throw Error('3D rendering is unavailable. Enable hardware acceleration in your browser; the figures below remain available.');
  context.getExtension('WEBGL_lose_context')?.loseContext();
  const window3d=vtkGenericRenderWindow.newInstance({background:[.925,.951,.965],listenWindowResize:false,defaultViewAPI:'WebGL'});
  window3d.setContainer(canvas);
  const renderer=window3d.getRenderer(), renderWindow=window3d.getRenderWindow(), camera=renderer.getActiveCamera();
  const lookup=vtkColorTransferFunction.newInstance();
  const actors=regions.map(region=>{
    const data=polyData(region.points,region.polygons), mapper=vtkMapper.newInstance();mapper.setInputData(data);mapper.setLookupTable(lookup);
    const actor=vtkActor.newInstance();actor.setMapper(mapper);
    actor.getProperty().set({ambient:.3,diffuse:.7,specular:.12,specularPower:15});
    renderer.addActor(actor);return {region,data,mapper,actor,cut:null,scalar:null};
  });
  const cube=vtkAnnotatedCubeActor.newInstance();
  cube.setDefaultStyle({fontColor:'#234b60',edgeColor:'#6e8999',edgeThickness:.025,faceColor:'#f6fafc'});
  for(const [method,text] of [['setXPlusFaceProperty','+Z'],['setXMinusFaceProperty','−Z'],['setYPlusFaceProperty','+Y'],['setYMinusFaceProperty','−Y'],['setZPlusFaceProperty','−X'],['setZMinusFaceProperty','+X']])cube[method]({text});
  const marker=vtkOrientationMarkerWidget.newInstance({actor:cube,interactor:window3d.getInteractor(),parentRenderer:renderer});
  marker.setViewportCorner(Corners.BOTTOM_LEFT);marker.setViewportSize(.16);marker.setMinPixelSize(65);marker.setMaxPixelSize(100);marker.setEnabled(true);
  let sectionY=null, mode='surface', frames=0;
  function reset(front=false) {
    camera.setFocalPoint(.35,-.025,.3);camera.setViewUp(0,0,1);camera.setParallelProjection(true);
    camera.setPosition(...(front?[.35,-2,.3]:[1.45,-1.8,1.25]));
    renderer.resetCamera(...model.bounds);renderer.resetCameraClippingRange();renderWindow.render();
  }
  function update() {
    const stage=controls.stage.value, fieldName=controls.field.value;
    const potential=controls.field.querySelector('option[value="potential"]');potential.disabled=stage!=='3';
    if(stage!=='3' && fieldName==='potential'){controls.field.value='stress';return update();}
    const field=FIELDS[fieldName], slicing=controls.view.value==='section', y=Number(controls.section.value);
    const rebuild=slicing && sectionY!==y;
    let range=field.range;
    if(fieldName==='temperature')range=stage==='1'?[249,251]:stage==='2'?[24,26]:[25,100];
    if(range){lookup.removeAllPoints();for(const [t,r,g,b] of PALETTE)lookup.addRGBPoint(range[0]+t*(range[1]-range[0]),r,g,b);lookup.setMappingRange(...range);lookup.updateRange();}
    const colored=fieldName!=='material';
    controls.opacity.disabled=fieldName==='temperature';
    for(const item of actors) {
      const {region,mapper,actor}=item;
      if(rebuild){item.cut?.data.delete();item.cut=section(region,y);}
      const data=slicing?item.cut.data:item.data;
      mapper.setInputData(data);
      const colorThis=colored && (!field.copper || region.material==='Copper');
      if(colorThis) {
        const raw=region.states[stage][fieldName];
        if(!raw)throw Error('Field unavailable in this state');
        const values=slicing?Float32Array.from(item.cut.samples,([a,b,t])=>raw[a]+t*(raw[b]-raw[a])):raw;
        item.scalar?.delete();item.scalar=vtkDataArray.newInstance({name:'display',values,numberOfComponents:1});
        data.getPointData().setScalars(item.scalar);mapper.setScalarModeToUsePointData();mapper.setColorModeToMapScalars();mapper.setScalarVisibility(true);mapper.setScalarRange(...range);
      } else mapper.setScalarVisibility(false);
      const hex=region.color.slice(1);actor.getProperty().setColor(...[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16)/255));
      actor.getProperty().setOpacity(colorThis || region.material==='Copper'?1:Number(controls.opacity.value));
      actor.getProperty().setEdgeVisibility(controls.edges.checked);actor.getProperty().setEdgeColor(.22,.34,.42);
      actor.getProperty().setLighting(!slicing && fieldName==='material');
      actor.setVisibility(checks.get(region.material).checked && data.getNumberOfPoints()>0);
    }
    if(slicing)sectionY=y;
    find('.vtk-section-controls').hidden=!slicing;find('output').textContent=y.toFixed(3)+' μm';
    find('.vtk-overlay b').textContent=field.label;
    find('.vtk-overlay span').textContent=model.stages.find(s=>s.id===stage).label+(slicing?` · Y = ${y.toFixed(3)} μm`:' · 3D surface');
    find('.vtk-legend').hidden=!colored;
    if(colored){find('.vtk-legend-title').textContent=field.label+' · '+field.unit;find('.vtk-colorbar').style.background=GRADIENT;const ticks=root.querySelectorAll('.vtk-range span');ticks[0].textContent=range[0];ticks[1].textContent=range[1];}
    if(mode!==controls.view.value){mode=controls.view.value;reset(slicing);}else{renderer.resetCameraClippingRange();renderWindow.render();}
    frames++;
    root.dataset.ready='true';root.dataset.field=fieldName;root.dataset.stage=stage;root.dataset.view=controls.view.value;
    root.dataset.visibleRegions=actors.filter(a=>a.actor.getVisibility()).length;
    root.dataset.cells=actors.reduce((sum,a)=>sum+a.mapper.getInputData().getNumberOfPolys(),0);
    root.dataset.renderCount=frames;
  }
  let pending=false;
  const schedule=()=>{if(!pending){pending=true;requestAnimationFrame(()=>{pending=false;update();});}};
  for(const control of Object.values(controls))control.addEventListener(control.type==='range'?'input':'change',schedule);
  for(const check of checks.values())check.addEventListener('change',schedule);
  root.querySelector('[data-action="copper"]').addEventListener('click',()=>{checks.forEach((c,m)=>c.checked=m==='Copper');update();});
  root.querySelector('[data-action="stack"]').addEventListener('click',()=>{checks.forEach(c=>c.checked=true);update();});
  root.querySelector('[data-action="reset"]').addEventListener('click',()=>reset(controls.view.value==='section'));
  root.querySelector('[data-action="front"]').addEventListener('click',()=>reset(true));
  root.addEventListener('vtk-field',event=>{if(event.detail==='potential')controls.stage.value='3';controls.field.value=event.detail;update();});
  canvas.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(event.key))return;
    event.preventDefault();
    if(event.key==='ArrowLeft')camera.azimuth(-10);if(event.key==='ArrowRight')camera.azimuth(10);
    if(event.key==='ArrowUp')camera.elevation(10);if(event.key==='ArrowDown')camera.elevation(-10);
    if(['+','='].includes(event.key))camera.zoom(1.15);if(event.key==='-')camera.zoom(1/1.15);
    camera.orthogonalizeViewUp();renderer.resetCameraClippingRange();renderWindow.render();
  });
  const observer=new ResizeObserver(()=>window3d.resize());observer.observe(canvas);
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();root.dataset.ready='false';find('.vtk-overlay span').textContent='3D context lost. Reload this page to restore the viewer.';},true);
  window3d.resize();reset();update();
}

for(const root of document.querySelectorAll('[data-vtk-model]')) {
  try {
    const model=window.SIMULATION_MODELS?.[root.dataset.vtkModel];
    if(!model)throw Error('The model data could not be loaded. Reload this page to try again.');
    mount(root,model);
  } catch(error) {
    root.dataset.error=error.message;
    root.replaceChildren();const message=document.createElement('div');message.className='vtk-status';message.setAttribute('role','alert');message.textContent=error.message;root.append(message);console.error('VTK viewer:',error);
  }
}
document.querySelectorAll('[data-explore-field]').forEach(link=>link.addEventListener('click',()=>{
  const root=document.querySelector('[data-vtk-model]');root?.dispatchEvent(new CustomEvent('vtk-field',{detail:link.dataset.exploreField}));
}));
