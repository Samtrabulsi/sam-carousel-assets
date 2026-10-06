import glob
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-Bold.otf',30); fr=ImageFont.truetype(F+'Inter-Regular.otf',22); fs=ImageFont.truetype(F+'Inter-SemiBold.otf',20); ft=ImageFont.truetype(F+'InterDisplay-Bold.otf',64)
GOLD=(172,203,255); BG=(8,13,23); W=(242,245,251); G=(174,186,205)
shots=[
('0:00–0:03','01 WHERE YOU ARE','Clean background, lines slide up one at a time: "Most experts are the best-kept secret."','Pad, ticks, bell'),
('0:03–0:04','01 WHERE YOU ARE','"Great at the work."','Bell + whoosh'),
('0:04–0:06','01 WHERE YOU ARE','"Invisible online." The word "online" fades away.','Pulse bass enters'),
('0:06–0:08','01 WHERE YOU ARE','"Doing it all alone."','Snare roll, riser, silence'),
('0:08–0:09','02 THE SHIFT','Flash. The chrome ribbon on its own (no text over it).','DROP: impact'),
('0:09–0:12','02 THE SHIFT','BRAND VICTORY 2.0 on a clean background. Mentorship · Done-For-You · AI Employees · CRM.','2.0 slam'),
('0:12–0:14','02 THE SHIFT (cream)','"Your brand." A real client profile.','Hit'),
('0:14–0:15','02 THE SHIFT (cream)','"Your message." A bubble types "Stop being the best-kept secret."','Hit'),
('0:15–0:17','02 THE SHIFT (cream)','"Your AI team." Four AI employees orbit.','Hit'),
('0:17–0:21','03 · 01 MENTORSHIP','Dr. Sam portrait + quote "Trust is what actually sells."','Whoosh + hit'),
('0:21–0:26','03 · 02 DONE FOR YOU (cream)','"We build it. You approve it." Brand / Content / Systems ticked.','Whoosh + hit'),
('0:26–0:31','03 · 03 AI EMPLOYEES','Receptionist, Follow-Up, Scheduler, Content: all ONLINE.','Whoosh + hit'),
('0:31–0:35','03 · 04 CRM & DASHBOARD','"Track everything. Boost what works. Automate the rest." The dashboard counts up and Boost switches ON.','Bell per line, toggle ping'),
('0:35–0:39','03 · 04 CRM & DASHBOARD','A lead moves New → Contacted → Booked → Client. Automation lights: Lead in → AI replies → Call booked → Follow-up.','Ticks per step'),
('0:39–0:44','04 REAL RESULTS','Wall of real client profiles + 14+ yrs · 676K · 3 markets.','Bell per stat'),
('0:44–0:47','04 REAL RESULTS (cream)','Saly Zalzali testimonial.','Warm breakdown'),
('0:47–0:49','04 REAL RESULTS (cream)','Laila Hankir testimonial.',''),
('0:49–0:53','05 WHERE YOU\'RE GOING','YOU ARE HERE → Clarity → Authority → "Trusted. Booked. Scaling with AI."','Build + riser'),
('0:53–1:00','06 APPLY','Clean background: "Apply today." Apply Now, samtrabulsi.com.','Final hit, ring-out'),
]
fs_=sorted(glob.glob('sb4/*.jpg')); cols=3; tw,th=600,338; pad=40; cap=150
rows=(len(fs_)+cols-1)//cols
Wd=cols*tw+(cols+1)*pad; Hd=200+rows*(th+cap+pad)+pad
im=Image.new('RGB',(Wd,Hd),BG); d=ImageDraw.Draw(im)
d.text((pad,50),'BRAND VICTORY 2.0',font=ft,fill=W); d.text((pad,130),'v4 · Clean text (no image behind words) · one clear chapter label · lines slide in one by one · + CRM & Dashboard',font=fr,fill=GOLD)
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
im.save('storyboard-v4.png'); im.convert('RGB').save('storyboard-v4.pdf')
print(im.size)
