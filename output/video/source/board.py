import glob
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-Bold.otf',30); fr=ImageFont.truetype(F+'Inter-Regular.otf',22); fs=ImageFont.truetype(F+'Inter-SemiBold.otf',20); ft=ImageFont.truetype(F+'InterDisplay-Bold.otf',64)
GOLD=(212,175,55); BG=(14,14,16); W=(240,236,226); G=(160,156,148)
shots=[
('0:00–0:07','COLD OPEN','"Most experts are invisible." — gold rule draws, words blur-rise; "invisible" literally fades away.','Pad + clock ticks + bells'),
('0:07–0:15','THE PROBLEM','"You\'re great at what you do." Pain chips pop in and get struck out one by one.','Pulse bass enters, stab on each strike'),
('0:15–0:18','THE TURN','"What if your brand worked as hard as you do?" Slow push-in, glow builds.','Snare roll starts, riser'),
('0:18–0:21','COUNTDOWN','3 · 2 · 1 in gold, blur-punch on each beat. Dust accelerates.','Hits on each number, pre-drop silence'),
('0:21–0:24','THE REVEAL','White flash + shockwave. "INTRODUCING" → BRAND VICTORY letters flip up.','DROP: impact + full anthem'),
('0:24–0:29','2.0 SLAM','"2.0" slams in with camera shake, light sweep, tagline "Become the obvious choice."','Second impact'),
('0:29–0:31','SECTION','"How it helps you win."','Whoosh'),
('0:31–0:35','01 POSITIONING','"Own a position no one can copy." Crosshair draws on, dot locks to centre.','Whoosh + hit per card'),
('0:35–0:39','02 MESSAGING','"Words that turn strangers into clients." Speech bubble types the line, hearts float.',''),
('0:39–0:43','03 CONTENT SYSTEM','"Content that brings clients to you." Post grid lights up, leads stream in.',''),
('0:43–0:47','04 PREMIUM OFFERS','"Charge what you\'re really worth." Gold bars rise, $ → $$$.','Progress bar completes'),
('0:47–0:53','TRANSFORMATION','"Invisible → In-Demand." Growth line draws: Clarity → Authority → Clients.','Breakdown, riser into CTA'),
('0:53–1:00','CALL TO ACTION','"Apply Today." Pulsing gold Apply Now button, "Limited spots", @samtrabulsi.','Final hit, chord rings out'),
]
fs_=sorted(glob.glob('sb/*.jpg')); cols=3; tw,th=600,338; pad=40; cap=150
rows=(len(fs_)+cols-1)//cols
Wd=cols*tw+(cols+1)*pad; Hd=200+rows*(th+cap+pad)+pad
im=Image.new('RGB',(Wd,Hd),BG); d=ImageDraw.Draw(im)
d.text((pad,50),'BRAND VICTORY 2.0',font=ft,fill=W); d.text((pad,130),'Launch film storyboard  ·  60s  ·  16:9  ·  120 BPM original score',font=fr,fill=GOLD)
def wrap(txt,font,w):
    out=[];line=''
    for wd in txt.split():
        t=(line+' '+wd).strip()
        if d.textlength(t,font=font)>w: out.append(line); line=wd
        else: line=t
    return out+[line]
for i,(f,s) in enumerate(zip(fs_,shots)):
    x=pad+(i%cols)*(tw+pad); y=200+(i//cols)*(th+cap+pad)
    im.paste(Image.open(f).resize((tw,th)),(x,y)); d.rectangle([x,y,x+tw,y+th],outline=(60,56,40))
    d.rectangle([x,y,x+70,y+34],fill=GOLD); d.text((x+12,y+5),f'{i+1:02d}',font=fs,fill=(10,10,10))
    d.text((x,y+th+12),s[1],font=fs,fill=GOLD); d.text((x+tw-d.textlength(s[0],font=fs),y+th+12),s[0],font=fs,fill=G)
    yy=y+th+42
    for ln in wrap(s[2],fr,tw)[:3]: d.text((x,yy),ln,font=fr,fill=W); yy+=28
    if s[3]: d.text((x,yy+2),'Music: '+s[3],font=fr,fill=G)
im.save('storyboard.png'); im.convert('RGB').save('storyboard.pdf')
print(im.size)
