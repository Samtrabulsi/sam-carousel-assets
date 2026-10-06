import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
const mode = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport:{width:1920,height:1080}, deviceScaleFactor:1 });
await page.goto('file://'+process.cwd()+'/scene.html');
await page.evaluate(()=>window.ready);
await page.waitForTimeout(500);
if (mode==='stills') {
  const dir=process.argv[3]; const ts = process.argv.slice(4).map(Number);
  for (const t of ts) { await page.evaluate(t=>render(t), t); await page.screenshot({path:`${dir}/t${t.toFixed(1).padStart(5,'0')}.jpg`, type:'jpeg', quality:85}); }
} else {
  const fps=30, total=60*fps;
  const ff = spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','video_only.mp4'],{stdio:['pipe','ignore','inherit']});
  for (let f=0; f<total; f++) {
    await page.evaluate(t=>render(t), f/fps);
    const buf = await page.screenshot({type:'jpeg', quality:92});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if (f%300===0) console.log('frame',f);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r));
}
await browser.close();
