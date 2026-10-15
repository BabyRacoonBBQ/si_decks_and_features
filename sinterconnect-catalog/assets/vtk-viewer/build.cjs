const fs=require('node:fs');
const path=require('node:path');
const esbuild=require('esbuild');
const out=__dirname;
const result=esbuild.buildSync({
  absWorkingDir:__dirname,entryPoints:[path.join(out,'viewer.mjs')],
  outfile:path.join(out,'vtk-model-viewer.js'),bundle:true,minify:true,
  format:'iife',platform:'browser',target:['chrome110','firefox115','safari16.4'],
  nodePaths:require.resolve.paths('@kitware/vtk.js'),metafile:true,legalComments:'linked',
  define:{'process.env.NODE_ENV':'"production"'},
});
const packages=new Map();
for(const input of Object.keys(result.metafile.inputs)){
  const normalized=input.replaceAll('\\','/'),start=normalized.lastIndexOf('node_modules/');
  if(start<0)continue;
  const parts=normalized.slice(start+'node_modules/'.length).split('/');
  const name=parts[0].startsWith('@')?parts.slice(0,2).join('/'):parts[0];
  if(packages.has(name))continue;
  const root=path.resolve(__dirname,normalized.slice(0,start)+'node_modules/'+name);
  const meta=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
  const licenses=fs.readdirSync(root).filter(f=>/^(license|copying)(\.|$)/i.test(f));
  packages.set(name,{name,version:meta.version,license:meta.license,root,licenses});
}
fs.writeFileSync(path.join(out,'THIRD_PARTY_LICENSES.txt'),[...packages.values()].map(p=>
  `${p.name} ${p.version} (${p.license})\n${'='.repeat(70)}\n`+
  p.licenses.map(f=>fs.readFileSync(path.join(p.root,f),'utf8')).join('\n')
).join('\n\n'));
fs.writeFileSync(path.join(out,'build-info.json'),JSON.stringify({
  entry:'viewer.mjs',vtkVersion:require('@kitware/vtk.js/package.json').version,
  esbuildVersion:esbuild.version,packages:[...packages.values()].map(({name,version,license})=>({name,version,license})),
  localFilesOnly:true,modelLoading:'classic script; no fetch, server or CDN required',
},null,2));
console.log(JSON.stringify({bundleBytes:fs.statSync(path.join(out,'vtk-model-viewer.js')).size,packages:[...packages.keys()]}));
