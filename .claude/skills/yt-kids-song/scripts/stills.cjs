// node stills.cjs <song-dir>/video.html <outdir> t1 t2 ...  -> one jpg per time (seconds)
const path = require('path'); const { chromium } = require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('ERR', e.message)); await p.addInitScript(() => { window.requestAnimationFrame = () => 0; });
  await p.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.load("600 40px Fredoka"));
  for (const t of process.argv.slice(4).map(Number)) { await p.evaluate(t => draw(t), t);
    await p.screenshot({ path: `${process.argv[3]}/t${String(t.toFixed(1)).padStart(6, '0')}.jpg`, type: 'jpeg', quality: 75 }); }
  await b.close(); })();
