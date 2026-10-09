// node stills.cjs page.html outdir  -> one still per beat at 70% through it
const path=require('path');const {chromium}=require(path.join(require('child_process').execSync('npm root -g').toString().trim(),'playwright'));
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
p.on('pageerror',e=>console.error('ERR',e.message));
await p.addInitScript(()=>{window.requestAnimationFrame=()=>0;});
await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.evaluate(()=>typeof imgReady!=="undefined"?imgReady:null);
const segs=await p.evaluate(()=>SEG.map(s=>[s.start,s.end]));
for(let i=0;i<segs.length;i++){const t=segs[i][0]+(segs[i][1]-segs[i][0])*0.7;await p.evaluate(t=>draw(t),t);
await p.screenshot({path:`${process.argv[3]}/b${String(i).padStart(2,'0')}.jpg`,type:'jpeg',quality:70});}
await b.close();})();
