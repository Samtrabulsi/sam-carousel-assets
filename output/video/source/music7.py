# Original launch soundtrack for Brand Victory 2.0 — synthesized from scratch (royalty-free).
# 120 BPM, A minor (Am - F - C - G), scored to the 60s storyboard.
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
DUR = 90.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def t_arr(d): return np.arange(int(d * SR)) / SR
def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i < 0: sig = sig[-i:]; i = 0
    if i >= N: return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gain * l * 1.414
    R[i:i + len(sig)] += sig * gain * r * 1.414
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def saw(f, t, ph=0.0): return 2 * ((f * t + ph) % 1) - 1
def adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, Rr = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n); e[:A] = np.linspace(0, 1, A)
    D = min(D, n - A); e[A:A + D] = np.linspace(1, s, D)
    if Rr and n > Rr: e[-Rr:] *= np.linspace(1, 0, Rr)
    return e

# ---- instruments ----
def kick(gain=1.0):
    t = t_arr(0.5); f = 45 + 110 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    s += 0.3 * np.exp(-t * 300) * rng.standard_normal(len(t))
    return np.tanh(s * 1.6) * gain
def clap():
    t = t_arr(0.35); n = rng.standard_normal(len(t))
    env = np.exp(-t * 18) + 0.6 * np.exp(-((t - 0.012) % 0.012) * 400) * (t < 0.036)
    return bp(n, 900, 4000) * env * 0.8
def hat(open_=False):
    t = t_arr(0.25 if open_ else 0.06); n = hp(rng.standard_normal(len(t)), 7000)
    return n * np.exp(-t * (12 if open_ else 70)) * 0.35
def supersaw(notes, d, cutoff=3000, voices=7, det=0.18):
    t = t_arr(d); s = np.zeros(len(t))
    for n in notes:
        f0 = midi(n)
        for v in range(voices):
            cents = (v - voices // 2) / (voices // 2) * det * 100
            s += saw(f0 * 2 ** (cents / 1200), t, rng.random())
    s /= (len(notes) * voices) ** 0.6
    return lp(s, cutoff, 2)
def pad(notes, d, cutoff=900):
    s = supersaw(notes, d, cutoff, 5, 0.12)
    return s * adsr(len(s), d * 0.35, 0.1, 1, d * 0.35)
def bass(n, d, cutoff=500):
    t = t_arr(d); f = midi(n)
    s = 0.6 * np.sin(2 * np.pi * f * t) + 0.4 * lp(saw(f, t), cutoff)
    return s * adsr(len(t), 0.005, 0.08, 0.7, 0.04)
def bell(n, d=1.6):
    t = t_arr(d); f = midi(n)
    s = np.sin(2 * np.pi * f * t + 1.5 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 4))
    return s * np.exp(-t * 2.6) * 0.5
def riser(d, f0=300, f1=6000):
    t = t_arr(d); n = rng.standard_normal(len(t))
    out = np.zeros(len(t)); seg = 2048
    for i in range(0, len(t), seg):
        fc = f0 * (f1 / f0) ** (i / len(t))
        out[i:i + seg] = bp(n[i:i + seg + 0], fc * 0.7, min(fc * 1.4, SR / 2 - 100))[: len(out[i:i + seg])]
    tone = saw(np.cumsum(np.linspace(110, 880, len(t))) / SR, 1.0)
    out = out + 0.15 * lp(np.sin(2 * np.pi * np.cumsum(np.linspace(110, 880, len(t))) / SR), 3000)
    return out * np.linspace(0, 1, len(t)) ** 2
def whoosh(d=0.8, rev=False):
    t = t_arr(d); n = rng.standard_normal(len(t))
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    s = bp(n, 400, 3500) * e * 0.5
    return s[::-1] if rev else s
def impact(gain=1.0):
    t = t_arr(3.5); f = 30 + 80 * np.exp(-t * 8)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)
    crash = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 2.2) * 0.35
    return np.tanh((boom * 1.5 + crash)) * gain
def tick():
    t = t_arr(0.03); return np.sin(2 * np.pi * 3000 * t) * np.exp(-t * 200) * 0.4

prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
roots = [45, 41, 36, 43]
mel = [76, 74, 72, 71, 72, 74, 76, 79]  # simple hook



# ===== V7 (90s reading-time cut) =====
S=[0,2.6,4.4,6.2,8.0,9.3,12.0,13.85,15.45,17.0,21.5,26.0,31.0,39.0,44.0,46.9,49.5,53.5,60.0]
LL=[4,2.5,3,3,1.5,4,3.5,3.5,3,7,6.5,6.5,11,6.5,5,5,6,8.5]
SEG=[]; R0=0.0
for i in range(len(LL)):
    D=S[i+1]-S[i]; E=min(1.3,D-0.5); A=E+0.45; H=D-A; SEG.append((S[i],D,E,A,H,R0,LL[i])); R0+=LL[i]
def W(t):   # scene time -> real time
    for (s0,D,E,A,H,r0,Lr) in SEG:
        if t < s0+D or (s0,D,E,A,H,r0,Lr)==SEG[-1]:
            u=t-s0
            if u<E: return r0+u
            if u<D-0.45: return r0+E+(u-E)*(Lr-A)/H
            return r0+Lr-(D-u)
    return 90.0
CUT=[sum(LL[:i]) for i in range(len(LL)+1)]
print('cuts',CUT)
# hook 0 -> drop
DROP=W(8.0)
add(pad([57,60,64,69], DROP+0.3, 800), 0.0, 0.35)
add(np.sin(2*np.pi*midi(33)*t_arr(DROP))*adsr(int(DROP*SR),1.5,.1,1,1.0), 0, 0.28)
for i in range(int(DROP/BEAT)): add(tick(), i*BEAT, 0.6 if i%2==0 else 0.35, 0.3*(-1)**i)
for a,n in ((0.15,76),(W(2.6),72),(W(4.4),69),(W(6.2),72)):
    add(whoosh(0.5), a-0.25, 0.45); add(bell(n), a, 0.3)
add(whoosh(0.9, rev=True), W(5.2), 0.4)
pb=W(4.4)
nb=int((DROP-2.0-pb)/BEAT)
for e in range(nb): add(bass(roots[(e//8)%4], BEAT/2*.9, 500), pb+e*BEAT/2, 0.33)
for q in range(int((DROP-pb)/BEAT)):
    if q%2==0: add(kick(0.6), pb+q*BEAT)
rt=DROP-2.0
while rt<DROP-0.15:
    pr=(rt-(DROP-2.0))/1.85; add(clap()*.5, rt, .25+.6*pr); rt+=BEAT/(2 if pr<.4 else 4 if pr<.75 else 8)
add(riser(2.0,400,8000), DROP-2.05, 0.45)
gs,ge=int((DROP-0.15)*SR),int(DROP*SR); L[gs:ge]*=np.linspace(1,0,ge-gs); R[gs:ge]*=np.linspace(1,0,ge-gs)
add(impact(1.0), DROP, 0.95); add(impact(0.7), W(9.6), 0.7)
def full_bars(start, nbars, kick_on=True, intensity=1.0):
    for bar in range(nbars):
        s = start + bar * BAR / 2  # one chord per 2 beats? -> keep 1 chord per bar of 2s
    for bar in range(nbars):
        s = start + bar * 2.0; c = bar % 4
        chord = prog[c] + [prog[c][0] + 12]
        sw = supersaw(chord, 2.0, 2600 * intensity + 800) * adsr(int(2 * SR), .005, .2, .85, .05)
        # sidechain pump
        tt = t_arr(2.0); pump = 1 - 0.7 * np.exp(-((tt % BEAT)) * 9)
        add(sw * pump, s, 0.30 * intensity, -0.15); add(sw * pump, s + 0.012, 0.30 * intensity, 0.15)
        for e in range(8):
            add(bass(roots[c] - 12 if e % 2 == 0 else roots[c], BEAT / 2 * 0.85, 900) * 1.0, s + e * BEAT / 2, 0.42)
        for q in range(4):
            if kick_on: add(kick(1.0), s + q * BEAT, 0.95)
            add(hat(open_=True), s + q * BEAT + BEAT / 2, 0.55, 0.3)
            for sub in (0.25, 0.75): add(hat(), s + q * BEAT + sub * BEAT, 0.35, -0.3)
        add(clap(), s + BEAT, 0.6); add(clap(), s + 3 * BEAT, 0.6)
        # hook melody
        for k in range(4):
            n = mel[(bar * 4 + k) % 8] if c != 3 else [74, 71, 74, 79][k]
            add(bell(n, 0.9) + 0.4 * bell(n + 12, 0.9), s + k * BEAT, 0.22 * intensity, 0.25)


BD=W(44.0)                      # testimonials breakdown start (real)
nbars=int((BD-DROP)//2)
full_bars(DROP, nbars, intensity=1.0)
fill=DROP+nbars*2
add(whoosh(0.8), fill, 0.5)
for k in range(4): add(clap()*.4, fill+k*BEAT/2, 0.3)
for a in (12.25,13.85,15.45): add(whoosh(0.6), W(a)-0.3, 0.6); add(impact(0.2), W(a), 0.3)
for a in (17.0,21.5,26.0,31.0,39.0): add(whoosh(0.7), W(a)-0.35, 0.7); add(impact(0.25), W(a)+0.05, 0.35)
for k in range(3): add(tick()*1.2, W(18.5+k*.2), 0.5)
for k in range(6): add(tick()*1.6, W(22.9+k*.32), 0.75); add(bell([76,78,80,81,83,85][k],0.5), W(22.9+k*.32), 0.12)
for i,a in enumerate((31.3,32.3,33.3)): add(bell(79+[0,2,5][i],1.0), W(a), 0.32)
add(bell(86,0.6), W(33.0), 0.2)
for a in (33.9,34.6,35.6,36.6): add(tick()*1.4, W(a), 0.7)
for a in (34.0,35.0,36.0): add(whoosh(0.35), W(a), 0.4)
for i in range(3): add(bell(84+[0,3,7][i],1.2), W(40.0+i*.4), 0.35)
# testimonials: warm breakdown
JR=W(49.5)
nb2=int(round((JR-BD)/2))
for bar in range(nb2):
    s=BD+bar*2.0; c=bar%4
    add(pad(prog[c]+[prog[c][0]+12],2.1,1600), s, 0.34)
    for e in range(8): add(bass(roots[c],BEAT/2*.85,500), s+e*BEAT/2, 0.28)
    for q in range(4): add(hat(), s+q*BEAT+BEAT/2, 0.35)
    for k in range(4): add(bell(mel[(bar*4+k)%8],0.9), s+k*BEAT, 0.16, 0.25)
for a in (44.3,46.9): add(whoosh(0.6), W(a)-0.3, 0.55)
# journey build
CTA=W(53.5)
nb3=int(round((CTA-JR)/2))
for bar in range(nb3):
    s=JR+bar*2.0; c=bar%4
    add(pad(prog[c]+[prog[c][0]+12],2.1,1500+bar*1000), s, 0.3)
    for q in range(4): add(kick(0.75), s+q*BEAT, 0.8)
for i,a in enumerate((50.96,51.6,52.2)): add(bell(81+[0,2,7][i],1.4), W(a), 0.35)
add(riser(2.6,500,8000), CTA-2.6, 0.38)
gs,ge=int((CTA-0.12)*SR),int(CTA*SR); L[gs:ge]*=np.linspace(1,0.1,ge-gs); R[gs:ge]*=np.linspace(1,0.1,ge-gs)
# CTA
add(impact(1.0), CTA, 0.95)
full_bars(CTA, 2, intensity=1.0)
END=CTA+4.0
add(kick(1.0), END, 0.9)
final=supersaw([57,60,64,69,76],4.0,3000)*np.exp(-t_arr(4.0)*0.9)
add(final,END,0.4); add(impact(0.6),END,0.6); add(bell(81,3.0),END,0.3); add(bell(88,3.0),END,0.18)
add(np.sin(2*np.pi*midi(33)*t_arr(4))*np.exp(-t_arr(4)*1.2),END,0.4)
# ---------- mix bus: reverb, glue, master ----------
ir_t = t_arr(2.2)
irL = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2); irR = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
irL = lp(irL, 6000); irR = lp(irR, 6000)
wetL = fftconvolve(L, irL)[:N]; wetR = fftconvolve(R, irR)[:N]
wetL /= np.max(np.abs(wetL)) + 1e-9; wetR /= np.max(np.abs(wetR)) + 1e-9
dryp = max(np.max(np.abs(L)), np.max(np.abs(R)))
mixL = L / dryp + 0.12 * wetL; mixR = R / dryp + 0.12 * wetR
mix = np.stack([mixL, mixR], 1)
mix = hp(mix.T, 28).T
mix = np.tanh(mix * 1.8) / np.tanh(1.8)          # soft-clip glue
fade = np.ones(N); fi = int(0.05 * SR); fo = int(1.2 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * 0.93
wavfile.write('music7.wav', SR, (mix * 32767).astype(np.int16))
print('ok', mix.shape)
