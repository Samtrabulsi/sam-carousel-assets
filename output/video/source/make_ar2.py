s=open('scene_ar.html').read()
def R(a,b,cnt=1):
    global s
    assert a in s, 'MISSING: '+a[:90]
    s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)
# CTA
R('<div class="kick" id="ck">Brand Victory 2.0 · Applications open</div>','<div class="kick" id="ck" style="font-size:36px"><span class="ltr">Brand Victory 2.0</span> · التسجيل مفتوح الآن</div>')
R('<span class="ln"><span>Apply <span class="it ice">today.</span></span></span>','<span class="ln"><span>قدّم <span class="it ice">اليوم.</span></span></span>')
R('<div class="btn" id="btn">Apply Now <span style="font-size:64px">↗</span></div>','<div class="btn" id="btn">قدّم الآن <span style="font-size:64px">↖</span></div>')
R('Mentorship · Done-For-You · AI Employees · CRM &amp; Dashboard','إرشاد · تنفيذ متكامل · موظفون بالذكاء الاصطناعي · <span class="ltr">CRM</span> ولوحة تحكم')
R('<div id="brand" style="position:absolute;bottom:56px;display:flex;','<div id="brand" style="direction:ltr;position:absolute;bottom:56px;display:flex;')
# chapters
R("""const CH=[[0,'Where you are'],[8,'The shift'],[17,'How we get you there'],[39,'Real results'],[49.5,"Where you're going"],[53.5,'Apply']];""",
  """const CH=[[0,'أين أنت الآن'],[8,'التحوّل'],[17,'كيف نوصلك'],[39,'نتائج حقيقية'],[49.5,'إلى أين تتجه'],[53.5,'قدّم الآن']];""")
# motion directions mirrored for RTL
R("el.style.transform=`translateX(${(1-pin)*1920*.35 - pout*1920*.35}px)`;","el.style.transform=`translateX(${-(1-pin)*1920*.35 + pout*1920*.35}px)`;")
R("v.style.transform=`translateX(${(1-pin)*200 - pout*120}px)`;","v.style.transform=`translateX(${-(1-pin)*200 + pout*120}px)`;")
R("c.style.transform=`translateX(${(1-p)*160}px)`;","c.style.transform=`translateX(${-(1-p)*160}px)`;")
R("x.style.letterSpacing=`${f*14}px`;","x.style.filter=`blur(${f*6}px)`;")
R("$('#strip').style.transform=`translateX(${lerp(1900,-1750,sp)}px) rotateY(-12deg)`;","$('#strip').style.transform=`translateX(${lerp(-3240,410,sp)}px) rotateY(12deg)`;")
# journey mirrored (x -> 1920-x)
R("const d='M280,850 C 440,850 540,770 720,720 S 1000,640 1160,560 S 1420,450 1580,420';","const d='M1640,850 C 1480,850 1380,770 1200,720 S 920,640 760,560 S 500,450 340,420';")
R('<stop offset="0" stop-color="#2d63f5"/><stop offset="1" stop-color="#accbff"/></linearGradient><radialGradient','<stop offset="0" stop-color="#accbff"/><stop offset="1" stop-color="#2d63f5"/></linearGradient><radialGradient')
R('''font-family="Varela Round" font-size="86" fill="#f2f5fb" letter-spacing="-1.5">From where you are <tspan font-family="Instrument Serif" font-style="italic" font-size="98" fill="#accbff">to where you're going.</tspan></text>''',
  '''font-family="Readex Pro" font-weight="600" font-size="80" fill="#f2f5fb" direction="rtl">من حيث أنت <tspan font-family="Amiri" font-weight="700" font-size="92" fill="#accbff">إلى حيث تتجه.</tspan></text>''')
R("[['Clarity',720,720,70,0,'middle'],['Authority',1160,560,-42,-30,'end']]","[['الوضوح',1200,720,76,0,'middle'],['المكانة',760,560,-40,30,'end']]")
R('''text-anchor="${an}" font-family="DM Sans" font-weight="700" font-size="44"''','''text-anchor="${an}" direction="rtl" font-family="Readex Pro" font-weight="600" font-size="46"''')
R('<g id="pinA" transform="translate(280,850)"','<g id="pinA" transform="translate(1640,850)"')
R('font-family="DM Sans" font-weight="800" font-size="30" letter-spacing="3" fill="#0a1020">YOU ARE HERE</text>','direction="rtl" font-family="Readex Pro" font-weight="700" font-size="34" fill="#0a1020">أنت هنا</text>')
R('font-family="DM Sans" font-weight="500" font-size="42" fill="#aebacd">Invisible.</text>','direction="rtl" font-family="IBM Plex Sans Arabic" font-weight="500" font-size="42" fill="#aebacd">غير مرئي.</text>')
R('font-family="DM Sans" font-weight="500" font-size="42" fill="#aebacd">Doing it all alone.</text>','direction="rtl" font-family="IBM Plex Sans Arabic" font-weight="500" font-size="42" fill="#aebacd">تفعل كل شيء وحدك.</text>')
R('<g id="pinB" transform="translate(1580,420)"','<g id="pinB" transform="translate(340,420)"')
R('''font-family="DM Sans" font-weight="800" font-size="30" letter-spacing="3" fill="#accbff">WHERE YOU'RE GOING</text>''','direction="rtl" font-family="Readex Pro" font-weight="700" font-size="34" fill="#accbff">إلى أين تتجه</text>')
R('font-family="Varela Round" font-size="52" fill="#f2f5fb">Trusted. Booked.</text>','direction="rtl" font-family="Readex Pro" font-weight="600" font-size="54" fill="#f2f5fb">موثوق. ومحجوز.</text>')
R('font-family="Varela Round" font-size="52" fill="#f2f5fb">Paid what you’re worth.</text>','direction="rtl" font-family="Readex Pro" font-weight="600" font-size="54" fill="#f2f5fb">وتتقاضى ما تستحق.</text>')
R("$('#pinA').setAttribute('transform',`translate(280,850) scale(${pa})`);","$('#pinA').setAttribute('transform',`translate(1640,850) scale(${pa})`);")
R("$('#pinB').setAttribute('transform',`translate(1580,420) scale(${pb})`);","$('#pinB').setAttribute('transform',`translate(340,420) scale(${pb})`);")
# chapter number isolated LTR
R("""$('#cnum').innerHTML=`<span style="color:${acc}">${String(idx+1).padStart(2,'0')}</span><small style="color:${ink}"> / 06</small>`;""",
  """$('#cnum').innerHTML=`<span style="color:${acc}">${String(idx+1).padStart(2,'0')}</span><small style="color:${ink}"> / 06</small>`; $('#cnum').style.direction='ltr';""")
open('scene_ar.html','w').write(s); print('ok')
