import glob
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-Bold.otf',30); fr=ImageFont.truetype(F+'Inter-Regular.otf',22); fs=ImageFont.truetype(F+'Inter-SemiBold.otf',20); ft=ImageFont.truetype(F+'InterDisplay-Bold.otf',64)
GOLD=(172,203,255); BG=(8,13,23); W=(242,245,251); G=(174,186,205)
shots=[
('0:00–0:03','01 WHERE YOU ARE','Hook over the chrome ribbon: "Most experts are the best-kept secret."','Dark pad, ticks, bell'),
('0:03–0:05','01 WHERE YOU ARE','"Great at the work."','Bell + whoosh per card'),
('0:05–0:07','01 WHERE YOU ARE','"Invisible online." The word "online" fades away.','Pulse bass enters'),
('0:07–0:09','01 WHERE YOU ARE','"Doing it all alone."','Snare roll + riser, silence'),
('0:09–0:10','02 THE SHIFT','Flash. A giant chrome "Meet".','DROP: impact'),
('0:10–0:13','02 THE SHIFT','BRAND VICTORY 2.0 over the ribbon: Mentorship + Done-For-You + Expert AI Employees.','2.0 slam'),
('0:13–0:15','02 THE SHIFT (cream)','"Your brand." A real client profile drops in.','Triplet hits'),
('0:15–0:17','02 THE SHIFT (cream)','"Your message." A bubble types "Stop being the best-kept secret."',''),
('0:17–0:19','02 THE SHIFT (cream)','"Your AI team." Four AI employees orbit.',''),
('0:19–0:21','03 HOW WE GET YOU THERE','"Three engines. One clear plan."','Whoosh'),
('0:21–0:25','03 · MENTORSHIP','Dr. Sam portrait, 14+ years badge, his line: "Trust is what actually sells."','Whoosh + hit'),
('0:25–0:30','03 · DONE FOR YOU (cream)','"We build it. You approve it." Brand / Content / Systems ticked.','Whoosh + hit'),
('0:30–0:36','03 · EXPERT AI EMPLOYEES','Receptionist, Follow-Up, Scheduler, Content: all ONLINE.','Whoosh + hit'),
('0:36–0:42','04 REAL RESULTS','A 3D wall of real client Instagram profiles. Counters: 14+ yrs · 676K · 3 markets.','Bell on each stat'),
('0:42–0:45','04 REAL RESULTS (cream)','Saly Zalzali testimonial with her profile.','Warm breakdown'),
('0:45–0:48','04 REAL RESULTS (cream)','Laila Hankir testimonial with her profile.',''),
('0:48–0:53','05 WHERE YOU\'RE GOING','YOU ARE HERE pin → Clarity → Authority → "Trusted. Booked. Scaling with AI."','Build + riser'),
('0:53–1:00','06 APPLY','"Apply today." Apply Now, samtrabulsi.com, BV logo, ribbon behind.','Final hit, ring-out'),
]
fs_=sorted(glob.glob('sb3/*.jpg')); cols=3; tw,th=600,338; pad=40; cap=150
rows=(len(fs_)+cols-1)//cols
Wd=cols*tw+(cols+1)*pad; Hd=200+rows*(th+cap+pad)+pad
im=Image.new('RGB',(Wd,Hd),BG); d=ImageDraw.Draw(im)
d.text((pad,50),'BRAND VICTORY 2.0',font=ft,fill=W); d.text((pad,130),'v3 · Faster hook · reveal at 0:09 · real client proof · navy/cream rhythm · -14 LUFS',font=fr,fill=GOLD)
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
im.save('storyboard-v3.png'); im.convert('RGB').save('storyboard-v3.pdf')
print(im.size)
