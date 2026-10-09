// Tamara as a photo puppet: animates Sam's own reference picture (Pixar-style render), no AI video needed.
// Files in the song folder: tamara-cutout.png (background removed), tamara-headmask.png, tamara-jawmask.png
// (made by make_photo_puppet.py). Motion: beat bounce + squash, sway, head tilt/nod, blinks, and a jaw
// that drops on sung vowels (the lower teeth/lip/chin slide down over a dark mouth opening).
//
// drawTamaraPhoto(ctx, opts) draws her with the feet's bottom-centre at (0,0), in source-image pixels (~1465 tall).
// opts: { t, beat, dance (bool), mouth ('X','A'..'F' as in tamara.js), blinkSeed }
(function () {
  const P = window.TAMARA_PHOTO = window.TAMARA_PHOTO || {
    // image-space landmarks of tamara-reference.webp (1024x1536)
    feet: [480, 1487], neck: [480, 440],
    split: [[422, 358], [484, 364], [546, 356]], // line between upper and lower teeth (left corner, middle, right corner)
    eyes: [{ x: 445, y: 250, rx: 36, ry: 27, rot: 0.12 }, { x: 567, y: 282, rx: 35, ry: 26, rot: 0.25 }],
    lid: '#E3A27A', lash: '#1E120C',
  };
  const load = src => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(null); im.src = src; });
  const masked = (img, mask) => { const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
    const x = cv.getContext('2d'); x.drawImage(img, 0, 0); x.globalCompositeOperation = 'destination-in'; x.drawImage(mask, 0, 0); return cv; };
  window.tamaraPhotoReady = Promise.all(['tamara-cutout.png', 'tamara-headmask.png', 'tamara-jawmask.png'].map(load)).then(([body, hm, jm]) => {
    if (!body) return; P.body = body; P.head = masked(body, hm); P.jaw = masked(body, jm);
  });
  const OPEN = { X: 0, A: 0.05, B: 0.35, C: 0.65, D: 1, E: 0.75, F: 0.3, G: 0.2, H: 0.5 };

  window.drawTamaraPhoto = function (c, o) {
    if (!P.body) return;
    const t = o.t || 0, beat = o.beat || 0, bph = beat * Math.PI;
    const b = o.dance ? Math.abs(Math.sin(bph)) : 0.5 + 0.5 * Math.sin(t * 2.4);
    const amp = o.dance ? 1 : 0.25;
    const sway = o.dance ? Math.sin(bph) * 0.045 : Math.sin(t * 0.9) * 0.015;
    // keep the head tilt small: the head layer sits on the body layer, so big angles show a double hair edge
    const tilt = o.dance ? Math.sin(bph * 0.5) * 0.018 : Math.sin(t * 1.3) * 0.01;
    const [fx, fy] = P.feet, [nx, ny] = P.neck;
    c.save();
    c.fillStyle = 'rgba(0,0,0,0.25)'; c.beginPath(); c.ellipse(0, 0, 230, 34, 0, 0, Math.PI * 2); c.fill(); // ground shadow
    c.rotate(sway); c.scale(1 + 0.018 * b * amp, 1 - 0.022 * b * amp); c.translate(0, -26 * b * amp);
    c.translate(-fx, -fy);
    c.drawImage(P.body, 0, 0);
    // head
    c.translate(nx, ny); c.rotate(tilt); c.translate(-nx, -ny);
    c.drawImage(P.head, 0, 0);
    // jaw: open the mouth
    const open = OPEN[o.mouth || 'X'] ?? 0, drop = open * 14;
    if (drop > 0.5) {
      const [l, m, r] = P.split, w = (r[0] - l[0]) / 2 * (0.64 - open * 0.08), cx = (l[0] + r[0]) / 2;
      c.save(); c.beginPath(); c.moveTo(l[0], l[1]); c.quadraticCurveTo(m[0], m[1] + 8, r[0], r[1]); c.lineTo(r[0], r[1] + 120); c.lineTo(l[0], l[1] + 120); c.closePath(); c.clip(); // below the upper teeth only
      c.fillStyle = '#4A1418'; c.beginPath(); c.ellipse(cx, m[1] + drop * 0.5 - 2, w, drop * 0.62 + 3, 0.05, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#C8505E'; c.beginPath(); c.ellipse(cx, m[1] + drop * 0.95, w * 0.5, drop * 0.3, 0.05, 0, Math.PI); c.fill(); // tongue
      c.restore();
      c.drawImage(P.jaw, 0, drop);
    }
    // blink every ~3.9 s
    const bp = (t + (o.blinkSeed || 0)) % 3.9, close = bp < 0.14 ? Math.sin(bp / 0.14 * Math.PI) : 0;
    if (close > 0.05) P.eyes.forEach(e => {
      c.save(); c.translate(e.x, e.y); c.rotate(e.rot);
      c.beginPath(); c.ellipse(0, 0, e.rx + 3, e.ry + 3, 0, 0, Math.PI * 2); c.clip();
      const lidY = -e.ry - 4 + (2 * e.ry + 8) * close * 0.55;
      c.fillStyle = P.lid; c.fillRect(-e.rx - 6, -e.ry - 6, 2 * e.rx + 12, lidY + e.ry + 6);
      c.restore();
      c.save(); c.translate(e.x, e.y); c.rotate(e.rot);
      c.strokeStyle = P.lash; c.lineWidth = 6; c.lineCap = 'round';
      const ly = -e.ry + (2 * e.ry) * close * 0.55; c.beginPath(); c.moveTo(-e.rx, ly - 2); c.quadraticCurveTo(0, ly + 8 * close, e.rx, ly - 2); c.stroke();
      c.restore();
    });
    c.restore();
  };
})();
