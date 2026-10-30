// Optional full-page geometry regression. No browser download or release writes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const browser = process.env.OHM_TEST_BROWSER;
const work = process.env.OHM_TEST_WORKDIR;
const release = path.resolve(process.env.OHM_TEST_RELEASE_ROOT || '../50ohm-site-releases');
const css = path.resolve(process.env.OHM_TEST_CSS || 'assets/style-course.css');
const measure = `<script>
addEventListener('load',()=>document.fonts.ready.then(()=>{
 const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width};};
 const blocks=[...document.querySelectorAll('.course .formula-block')].map(b=>({
  box:rect(b),previous:rect(b.previousElementSibling),
  column:rect([...b.closest('.course').children].find(e=>e.tagName==='P')),
  ink:[...b.querySelectorAll('.katex-html > .base')].map(rect),
  clientWidth:b.clientWidth,scrollWidth:b.scrollWidth
 }));
 const out=document.createElement('script');out.id='layout-result';out.type='application/json';
 out.textContent=JSON.stringify({blocks,errors:document.querySelectorAll('.katex-error').length});document.body.append(out);
 document.querySelector('.formula-block')?.scrollIntoView({block:'center'});
}));</script>`;
for (const lang of ['de','fr','it']) for (const width of [1600,1024,760,390]) {
 test(`${lang} complete course page, viewport ${width}`, {skip:!browser?'Set OHM_TEST_BROWSER and OHM_TEST_WORKDIR':false},()=>{
  assert.ok(work,'OHM_TEST_WORKDIR must name an explicit scratch directory');
  const run=path.resolve(work,`${lang}-${width}`);fs.mkdirSync(run,{recursive:true});
  const page=path.join(release,lang,'NE_spitze_effektiv_wert.html');
  const html=fs.readFileSync(page,'utf8')
   .replace('<head>','<head><base href="'+pathToFileURL(path.dirname(page)+'/').href+'">')
   .replace(/href="assets\/style-course\.css[^"\n]*"/,'href="'+pathToFileURL(css).href+'"')
   .replace('</body>',measure+'</body>');
  const input=path.join(run,'page.html');fs.writeFileSync(input,html);
  const result=spawnSync(browser,['--no-sandbox','--disable-gpu','--disable-background-networking',
   `--window-size=${width},1100`,`--user-data-dir=${path.join(run,'profile')}`,
   '--dump-dom','--virtual-time-budget=3000',pathToFileURL(input).href],{encoding:'utf8',timeout:40000,maxBuffer:16*1024*1024});
  fs.writeFileSync(path.join(run,'browser.log'),result.stderr||'');
  assert.equal(result.status,0,result.error?.message || result.stderr);
  const match=result.stdout.match(/<script id="layout-result" type="application\/json">([\s\S]*?)<\/script>/);
  assert.ok(match,'Browser must finish font loading and geometry measurement');
  const data=JSON.parse(match[1]);fs.writeFileSync(path.join(run,'measurements.json'),JSON.stringify(data,null,2));
  assert.equal(data.errors,0,'KaTeX errors');assert.ok(data.blocks.length>=4,'Expected real page formulas');
  for (const [i,b] of data.blocks.entries()) {
   const label=`formula ${i+1}`;
   assert.ok(Math.abs(b.box.width-b.column.width)<1,`${label}: text column width`);
   assert.ok(Math.abs(b.box.left-b.column.left)<1,`${label}: text column alignment`);
   assert.ok(b.box.top-b.previous.bottom<45,`${label}: pushed below floated margin`);
   for(const ink of b.ink){
    assert.ok(ink.top>=b.box.top-1 && ink.bottom<=b.box.bottom+1,`${label}: vertical clipping`);
    if(b.scrollWidth<=b.clientWidth+1)
     assert.ok(ink.left>=b.box.left-1 && ink.right<=b.box.right+1,`${label}: horizontal clipping`);
   }
  }
 });
}
