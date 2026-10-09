// Tamara as a photo puppet: animates Sam's own reference picture (Pixar-style render) for free, on CPU.
// v2: a smooth WebGL warp of the whole picture (no cut-out pieces, so no seams):
//   - hip sway that bends the body from planted feet, knee dip on the beat, breathing chest
//   - head tilt that fades out through the neck, hair ends that swing a moment behind the body
//   - lips that part while singing (opening tapers into the mouth corners, lower lip/chin stretch smoothly)
//   - blinks that pull real eyelid skin down over the eye
//   - several pose pictures (sing, point, cheer, clap, wave), cross-faded when the pose changes
// Pose pictures + landmarks live in youtube/kids-songs/characters/tamara/ (poses.json). build_song.py embeds the
// cutouts as tamara-cutout.js (window.TAMARA_POSES with data URLs), because WebGL refuses file:// textures.
//
// drawTamaraPhoto(ctx, opts) draws her with the feet's bottom-centre at (0,0) in source-image pixels.
// opts: { t, beat, pose, prevPose, poseK (0..1 cross-fade into pose), danceAmt (0..1), open (0..1 mouth), blinkSeed }
(function () {
  const POSES = window.TAMARA_POSES || {}; // name -> {src, feet, neck, chest, split|null, eyes}
  const PAD = [140, 70];
  const VS = 'attribute vec2 a; varying vec2 uv; void main(){ uv = a * 0.5 + 0.5; gl_Position = vec4(a, 0.0, 1.0); }';
  const FS = `precision highp float;
  uniform sampler2D tex; uniform vec2 size, pad, feet, neck, chest; uniform vec3 sp0, sp1, sp2;
  uniform vec4 eyeA, eyeB; uniform float rotA, rotB;
  uniform float bend, bob, tilt, breath, hair, mouth, blink, hasMouth;
  varying vec2 uv;
  vec4 S(vec2 p) { if (p.x < 0.0 || p.y < 0.0 || p.x > size.x || p.y > size.y) return vec4(0.0); return texture2D(tex, p / size); }
  float splitY(float x) { // smooth curve through the three split points
    float t = clamp((x - sp0.x) / (sp2.x - sp0.x), 0.0, 1.0);
    float c = sp1.y - 0.5 * (sp0.y + sp2.y);
    return mix(sp0.y, sp2.y, t) + c * (1.0 - pow(2.0 * t - 1.0, 2.0));
  }
  vec4 eyelid(vec2 p, vec4 e, float r, vec4 col) {
    vec2 d = p - e.xy; float cs = cos(-r), sn = sin(-r); vec2 l = vec2(cs * d.x - sn * d.y, sn * d.x + cs * d.y);
    float inside = (l.x * l.x) / (e.z * e.z * 1.25) + (l.y * l.y) / (e.w * e.w * 1.3);
    if (inside > 1.0 || blink <= 0.02) return col;
    float edge = -e.w * 1.15 + 2.3 * e.w * blink;               // lid edge moves down as the eye closes
    float k = smoothstep(edge + 1.5, edge - 1.5, l.y) * smoothstep(1.0, 0.75, inside);
    vec2 sl = vec2(l.x * 0.92, -e.w * 1.25 - 8.0 - (edge - l.y) * 0.25); // skin just above the lashes
    vec2 s = e.xy + vec2(cos(r) * sl.x - sin(r) * sl.y, sin(r) * sl.x + cos(r) * sl.y);
    vec4 skin = S(s);
    col = mix(col, vec4(skin.rgb * (0.94 + 0.06 * clamp((l.y - edge) / e.w + 1.0, 0.0, 1.0)), 1.0), k);
    float lash = smoothstep(3.2, 0.8, abs(l.y - edge)) * smoothstep(1.0, 0.7, inside) * step(0.15, blink);
    return mix(col, vec4(0.12, 0.07, 0.05, 1.0), lash * 0.9);
  }
  void main() {
    vec2 q = vec2(uv.x * (size.x + 2.0 * pad.x), (1.0 - uv.y) * (size.y + 2.0 * pad.y)) - pad;
    vec2 p = q;
    float h = clamp((feet.y - p.y) / (feet.y - 120.0), 0.0, 1.0);
    p.x -= bend * h * h;                                         // body bends from the feet
    float k = smoothstep(feet.y - 40.0, feet.y - 520.0, p.y);
    p.y -= bob * 16.0 * k;                                       // knee dip: everything above the knees drops
    vec2 dc = p - chest; float wc = exp(-dot(dc, dc) / (2.0 * 170.0 * 170.0));
    p = chest + dc / (1.0 + breath * 0.022 * wc);                // breathing
    float wh = smoothstep(520.0, 400.0, p.y);                    // head + top of hair, fading through the neck
    vec2 dn = p - neck; float a = -tilt * wh, ca = cos(a), sa = sin(a);
    p = neck + vec2(ca * dn.x - sa * dn.y, sa * dn.x + ca * dn.y);
    float side = smoothstep(130.0, 230.0, abs(p.x - neck.x));
    p.x -= hair * 16.0 * smoothstep(430.0, 760.0, p.y) * side;   // hair ends swing
    // mouth: lower lip / chin slide down, the gap shows the inside of the mouth
    float sy = splitY(p.x), d = p.y - sy;
    float wx = 1.0 - smoothstep(26.0, 56.0, abs(p.x - sp1.x));
    float wy = 1.0 - smoothstep(14.0, 95.0, d);
    float disp = hasMouth * mouth * 9.0 * wx * wy * step(-2.0, d);
    vec2 src = vec2(p.x, p.y - disp);
    vec4 col = S(src);
    float gap = src.y - splitY(src.x);
    if (disp > 0.3 && d >= -1.0 && gap < 0.0) {
      float depth = clamp(-gap / max(disp, 0.001), 0.0, 1.0);
      vec3 inner = mix(vec3(0.42, 0.12, 0.13), vec3(0.24, 0.05, 0.07), smoothstep(0.0, 0.6, depth));
      inner = mix(inner, vec3(0.80, 0.38, 0.42), smoothstep(0.55, 0.15, depth) * 0.6 * step(0.5, mouth)); // tongue near the lower lip
      float soft = smoothstep(0.0, 1.5, -gap) * smoothstep(0.0, 0.4, wx);
      col = mix(col, vec4(inner, 1.0), soft);
    }
    col = eyelid(p, eyeA, rotA, col);
    col = eyelid(p, eyeB, rotB, col);
    gl_FragColor = col;
  }`;

  let gl, prog, cv, U = {};
  const loadImg = src => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(null); im.src = src; });
  window.tamaraPhotoReady = Promise.all(Object.entries(POSES).map(([n, p]) => loadImg(p.src).then(img => [n, img]))).then(list => {
    list = list.filter(x => x[1]); if (!list.length) return;
    const W = Math.max(...list.map(x => x[1].width)), H = Math.max(...list.map(x => x[1].height));
    cv = document.createElement('canvas'); cv.width = W + 2 * PAD[0]; cv.height = H + 2 * PAD[1];
    gl = cv.getContext('webgl', { premultipliedAlpha: false, preserveDrawingBuffer: true, alpha: true });
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(s)); return s; };
    prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog); gl.useProgram(prog);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    'size pad feet neck chest sp0 sp1 sp2 eyeA eyeB rotA rotB bend bob tilt breath hair mouth blink hasMouth'.split(' ').forEach(n => U[n] = gl.getUniformLocation(prog, n));
    list.forEach(([n, img]) => { const tx = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tx);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      [gl.TEXTURE_MIN_FILTER, gl.TEXTURE_MAG_FILTER].forEach(f => gl.texParameteri(gl.TEXTURE_2D, f, gl.LINEAR));
      [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach(f => gl.texParameteri(gl.TEXTURE_2D, f, gl.CLAMP_TO_EDGE));
      POSES[n].tex = tx; POSES[n].w = img.width; POSES[n].h = img.height; });
    gl.uniform2f(U.pad, PAD[0], PAD[1]); gl.viewport(0, 0, cv.width, cv.height);
  });

  function renderPose(P, m) { // warp one pose picture into the GL canvas
    gl.bindTexture(gl.TEXTURE_2D, P.tex);
    gl.uniform2f(U.size, P.w, P.h); gl.uniform2f(U.feet, ...P.feet); gl.uniform2f(U.neck, ...P.neck); gl.uniform2f(U.chest, ...P.chest);
    const sp = P.split || [[0, 0], [1, 0], [2, 0]]; sp.forEach((s, i) => gl.uniform3f(U['sp' + i], s[0], s[1], 0));
    gl.uniform1f(U.hasMouth, P.split ? 1 : 0);
    gl.uniform4f(U.eyeA, ...P.eyes[0].slice(0, 4)); gl.uniform1f(U.rotA, P.eyes[0][4]);
    gl.uniform4f(U.eyeB, ...P.eyes[1].slice(0, 4)); gl.uniform1f(U.rotB, P.eyes[1][4]);
    Object.entries(m).forEach(([k, v]) => gl.uniform1f(U[k], v));
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  window.drawTamaraPhoto = function (c, o) {
    if (!cv) return;
    const pick = n => POSES[n] && POSES[n].tex ? POSES[n] : POSES.sing;
    const t = o.t || 0, bph = (o.beat || 0) * Math.PI, D = o.danceAmt || 0, I = 1 - D;
    const bp = (t + (o.blinkSeed || 0)) % 3.9, blink = bp < 0.18 ? Math.sin(bp / 0.18 * Math.PI) : 0;
    const m = {
      bend: D * 26 * Math.sin(bph) + I * 7 * Math.sin(t * 0.8),
      bob: D * Math.pow(Math.abs(Math.sin(bph)), 1.5),
      tilt: D * 0.035 * Math.sin(bph * 0.5 + 0.6) + I * (0.022 * Math.sin(t * 1.1) + 0.01 * Math.sin(t * 2.3)),
      hair: D * Math.sin(bph - 0.9) + I * 0.35 * Math.sin(t * 0.8 - 0.9),
      breath: 0.5 + 0.5 * Math.sin(t * 1.7), mouth: o.open || 0, blink: Math.min(1, blink * 1.15),
    };
    c.save();
    c.fillStyle = 'rgba(0,0,0,0.25)'; c.beginPath(); c.ellipse(0, 0, 230 - m.bob * 10, 34, 0, 0, Math.PI * 2); c.fill();
    const k = o.poseK ?? 1, cur = pick(o.pose), prev = pick(o.prevPose);
    const layers = k < 1 && prev !== cur ? [[prev, 1 - k], [cur, k]] : [[cur, 1]];
    for (const [P, alpha] of layers) {
      renderPose(P, m);
      c.globalAlpha = alpha; c.drawImage(cv, -P.feet[0] - PAD[0], -P.feet[1] - PAD[1]);
    }
    c.restore();
  };

  // Smoothed mouth opening from the sung words: average of the last few frames, so the lips don't flicker.
  const OPEN = { X: 0, A: 0.1, B: 0.45, C: 0.75, D: 1, E: 0.8, F: 0.4 };
  window.tamaraOpen = function (words, t) {
    let s = 0; for (let i = 0; i < 4; i++) s += OPEN[tamaraMouth(words, t - i / 30)] ?? 0; return s / 4;
  };
})();
