import glob
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-Bold.otf',30); fr=ImageFont.truetype(F+'Inter-Regular.otf',22); fs=ImageFont.truetype(F+'Inter-SemiBold.otf',20); ft=ImageFont.truetype(F+'InterDisplay-Bold.otf',64)
GOLD=(172,203,255); BG=(8,13,23); W=(242,245,251); G=(174,186,205)
shots=[
('0:00–0:07','01 WHERE YOU ARE','"You\'re the expert. But you\'re invisible." The word "invisible" literally fades away.','Pad, clock ticks, bells'),
('0:07–0:15','01 WHERE YOU ARE','"And you\'re doing it all yourself." Four pain points pop in and get struck out.','Pulse bass, stab on each strike'),
('0:15–0:18','02 THE SHIFT','"What if you had a mentor and a team that never sleeps?"','Snare roll, riser'),
('0:18–0:21','02 THE SHIFT','3 · 2 · 1 countdown in blue chrome.','Hit on each number, pre-drop silence'),
('0:21–0:24','02 THE SHIFT','Flash + shockwave. "INTRODUCING" → BRAND VICTORY in chrome letters.','DROP: impact + full anthem'),
('0:24–0:29','02 THE SHIFT','"2.0" slams in. "Mentorship + Done-For-You, powered by expert AI employees."','Second impact'),
('0:29–0:31','03 HOW WE GET YOU THERE','"Two engines. One clear plan."','Whoosh'),
('0:31–0:36','03 · MENTORSHIP','"Sam in your corner." 1:1 strategy. Compass needle swings to true north.','Whoosh + hit'),
('0:36–0:41','03 · DONE FOR YOU','"We build it. You approve it." Brand / Content / Systems get ticked off.','Whoosh + hit'),
('0:41–0:47','03 · EXPERT AI EMPLOYEES','"Your AI team, working 24/7." Receptionist, Follow-Up, Scheduler, Content: all ONLINE.','Whoosh + hit'),
('0:47–0:53','04 WHERE YOU\'RE GOING','YOU ARE HERE pin → route through Clarity & Authority → "Trusted. Booked. Scaling with AI."','Breakdown, bell per milestone, riser'),
('0:53–1:00','05 APPLY','"Apply today." Apply Now button, samtrabulsi.com, BV logo.','Final hit, chord rings out'),
]
fs_=sorted(glob.glob('sb2/*.jpg')); cols=3; tw,th=600,338; pad=40; cap=150
rows=(len(fs_)+cols-1)//cols
Wd=cols*tw+(cols+1)*pad; Hd=200+rows*(th+cap+pad)+pad
im=Image.new('RGB',(Wd,Hd),BG); d=ImageDraw.Draw(im)
d.text((pad,50),'BRAND VICTORY 2.0',font=ft,fill=W); d.text((pad,130),'v2 · Mentorship + Done-For-You + Expert AI Employees  ·  60s  ·  16:9  ·  site colours',font=fr,fill=GOLD)
def wrap(txt,font,w):
    out=[];line=''
    for wd in txt.split():
        t=(line+' '+wd).strip()
        if d.textlength(t,font=font)>w: out.append(line); line=wd
        else: line=t
    return out+[line]
for i,(f,s) in enumerate(zip(fs_,shots)):
    x=pad+(i%cols)*(tw+pad); y=200+(i//cols)*(th+cap+pad)
    im.paste(Image.open(f).resize((tw,th)),(x,y)); d.rectangle([x,y,x+tw,y+th],outline=(38,50,70))
    d.rectangle([x,y+th-34,x+70,y+th],fill=GOLD); d.text((x+12,y+th-29),f'{i+1:02d}',font=fs,fill=(8,13,23))
    d.text((x,y+th+12),s[1],font=fs,fill=GOLD); d.text((x+tw-d.textlength(s[0],font=fs),y+th+12),s[0],font=fs,fill=G)
    yy=y+th+42
    for ln in wrap(s[2],fr,tw)[:3]: d.text((x,yy),ln,font=fr,fill=W); yy+=28
    if s[3]: d.text((x,yy+2),'Music: '+s[3],font=fr,fill=G)
im.save('storyboard-v2.png'); im.convert('RGB').save('storyboard-v2.pdf')
print(im.size)
