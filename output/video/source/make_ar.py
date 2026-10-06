s=open('scene6.html').read()
def R(a,b,cnt=1):
    global s
    assert a in s, 'MISSING: '+a[:90]
    s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)

R('<html><head>','<html dir="rtl" lang="ar"><head>')
R('family=Varela+Round&','family=Varela+Round&family=Readex+Pro:wght@400;500;600;700&family=Amiri:wght@400;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&')
rtl_css='''
/* ===== ARABIC / RTL OVERRIDES ===== */
#stage{font-family:'IBM Plex Sans Arabic',sans-serif}
.H,.big,.ttl,.dlines .ln,.tq .q,.card .role,.svc .nm,.bubble,.bub2,#you,#tag1{font-family:'Readex Pro',sans-serif!important;letter-spacing:0!important}
.H{line-height:1.32;font-weight:600}
.big{line-height:1.25;font-weight:600}
.ttl{line-height:1.3;font-weight:600}
.it{font-family:'Amiri',serif!important;font-style:normal!important;font-weight:700;font-size:1.08em}
.ln{padding:.06em .08em .22em}
.kick,.tag,#chap .nm div,.card .on,.col h4,#sambadge,.mchips span,.stat .l,#dash .bar span,#dash .bar em{letter-spacing:0!important}
.ltr{direction:ltr;unicode-bidi:isolate;display:inline-block}
#chap{left:auto;right:90px}
#chap .nm div{left:auto;right:0}
#chap .segs i b{transform-origin:right}
.logo,.ver,.num,.stat .v,.kpi .v,#cnum{direction:ltr;unicode-bidi:isolate}
.big{left:auto;right:150px}
.vis2{right:auto;left:110px}
.bubble{left:auto;right:0;border-radius:40px 40px 8px 40px;transform-origin:100% 100%}
.bub2{left:auto;right:330px;border-radius:40px 40px 40px 8px;transform-origin:0 100%}
.ailbl{font-size:34px}
.feat .txt{left:auto;right:150px}
#samwrap{right:auto;left:190px}
#sambadge{left:50%}
#svc{right:auto;left:140px}
.svc .ok{right:auto;left:24px}
.cards{right:auto;left:130px}
.card .on{right:auto;left:28px}
.card .on b{margin-right:0;margin-left:10px}
#dash{right:auto;left:100px}
#dash .bar span{margin-left:0;margin-right:16px}
#dash .bar em{margin-left:0;margin-right:auto;font-size:20px}
.tog{right:auto;left:24px}
.wire i{transform-origin:right}
.dlines{left:auto;right:130px;width:720px}
.dlines .ln{font-size:76px;line-height:1.3}
.tq .ph{left:auto;right:170px;transform:rotate(4deg)}
.tq .qt{left:150px;right:800px}
.tq .q{font-size:68px;line-height:1.35}
.tq .q em{font-family:'Amiri',serif;font-style:normal;font-weight:700}
.quote{font-family:'Amiri',serif;font-style:normal;font-size:50px;line-height:1.45}
.sub,.bsub{line-height:1.5}
.lead{font-size:24px}
</style>'''
R('</style>',rtl_css)

# ---- copy ----
R('<span class="ln"><span>Most experts aren’t paid</span></span><span class="ln"><span>what they’re <span class="it ice">worth.</span></span></span>',
  '<span class="ln"><span>معظم الخبراء لا يتقاضون</span></span><span class="ln"><span>ما <span class="it ice">يستحقّون.</span></span></span>')
R('<span class="ln"><span>Great at the <span class="it ice">work.</span></span></span>','<span class="ln"><span>بارع في <span class="it ice">عملك.</span></span></span>')
R('<span class="ln"><span>Invisible <span class="it ice" id="h3x">online.</span></span></span>','<span class="ln"><span>غائب <span class="it ice" id="h3x">على الإنترنت.</span></span></span>')
R('<span class="ln"><span>Doing it all <span class="it ice">alone.</span></span></span>','<span class="ln"><span>تفعل كل شيء <span class="it ice">وحدك.</span></span></span>')
R('Mentorship · Done-For-You · <span class="it ice">AI Employees</span> · CRM','إرشاد · تنفيذ متكامل · <span class="it ice">موظفون بالذكاء الاصطناعي</span> · <span class="ltr">CRM</span>')
# triplet
R('<span class="ln"><span>Your</span></span><span class="ln"><span class="it cb">brand.</span></span><div class="bsub">Positioning. Identity.<br>A profile people trust.</div>',
  '<span class="ln"><span class="it cb" style="font-size:1.25em">علامتك.</span></span><div class="bsub">تموضع. هوية.<br>وحضور يثق به الناس.</div>')
R('<span class="ln"><span>Your</span></span><span class="ln"><span class="it cb">message.</span></span><div class="bsub">Words that sell<br>your expertise.</div>',
  '<span class="ln"><span class="it cb" style="font-size:1.25em">رسالتك.</span></span><div class="bsub">كلمات تبيع<br>خبرتك.</div>')
R('Clear. Confident.<br>Unmistakably you.','واضحة. واثقة.<br>وتشبهك تماماً.')
R('<span class="ln"><span>Your</span></span><span class="ln"><span class="it cb">AI team.</span></span><div class="bsub">Working for you,<br>day and night.</div>',
  '<span class="ln"><span class="it cb" style="font-size:1.1em">فريقك الذكي.</span></span><div class="bsub">يعمل لأجلك<br>ليلاً ونهاراً.</div>')
R('<div id="you">You</div>','<div id="you">أنت</div>')
R("['Reception','Follow-up','Scheduling','Content']","['الاستقبال','المتابعة','المواعيد','المحتوى']")
R("const msg='Get paid what you’re worth.';","const msg='احصل على ما تستحقّه.';")
# mentorship
R('<div class="tag">Mentorship</div><div class="ttl">Dr. Sam, <span class="it ice">in your corner.</span></div>','<div class="tag">الإرشاد</div><div class="ttl">د. سام، <span class="it ice">إلى جانبك.</span></div>')
R('“AI makes you faster. Systems make you consistent. Trust is what actually sells.”','«الذكاء الاصطناعي يمنحك السرعة. الأنظمة تمنحك الاستمرارية. والثقة هي ما يبيع فعلاً.»')
R('<span>Pricing strategy</span><span>Premium offers</span><span>Positioning</span>','<span>استراتيجية التسعير</span><span>عروض مميّزة</span><span>التموضع</span>')
R('<div id="sambadge">14+ YEARS BUILDING BRANDS</div>','<div id="sambadge"><span class="ltr">+14</span> عاماً في بناء العلامات</div>')
# DFY
R('<div class="tag">Done For You</div><div class="ttl">We build it.<br><span class="it cb">You approve it.</span></div><div class="sub">Everything you need to sell,<br>handled by our team.</div>',
  '<div class="tag">تنفيذ متكامل</div><div class="ttl">نحن ننفّذ.<br><span class="it cb">وأنت توافق.</span></div><div class="sub">كل ما تحتاجه لتبيع،<br>يتولّاه فريقنا.</div>')
R("[['$','Pricing'],['★','Offers'],['▤','Courses'],['▶','Video editing'],['↗','Ads & boosting'],['✎','Content']]",
  "[['$','التسعير'],['★','العروض'],['▤','الدورات'],['▶','مونتاج الفيديو'],['↗','الإعلانات والترويج'],['✎','المحتوى']]")
# AI employees
R('<div class="tag">Expert AI Employees</div><div class="ttl" style="font-size:96px">Your AI team, <span class="it ice">working 24/7.</span></div><div class="sub">Every enquiry answered. Every lead followed up.</div>',
  '<div class="tag">موظفون خبراء بالذكاء الاصطناعي</div><div class="ttl" style="font-size:92px">فريقك الذكي، <span class="it ice">يعمل <span class="ltr">24/7</span>.</span></div><div class="sub">كل استفسار يُجاب. وكل عميل محتمل يُتابَع.</div>')
for a,b in [('AI Receptionist','موظف الاستقبال الذكي'),('Answers every enquiry','يجيب عن كل استفسار'),('AI Follow-Up','المتابعة الذكية'),('Nurtures every lead','يتابع كل عميل محتمل'),
            ('AI Scheduler','منسّق المواعيد الذكي'),('Books your appointments','يحجز مواعيدك'),('AI Content Assistant','مساعد المحتوى الذكي'),('Keeps you visible','يبقيك حاضراً')]:
    R('>'+a+'<','>'+b+'<')
R('<b></b>ONLINE','<b></b>متصل',0)
# CRM
R('<div class="tag" id="d_tag">04 · CRM &amp; Dashboard</div>','<div class="tag" id="d_tag"><span class="ltr">04</span> · نظام <span class="ltr">CRM</span> ولوحة التحكم</div>')
R('<span id="dl1">Track everything.</span>','<span id="dl1">تابِع كل شيء.</span>')
R('<span id="dl2">Boost what works.</span>','<span id="dl2">عزّز ما ينجح.</span>')
R('<span id="dl3">Automate the rest.</span>','<span id="dl3">وأتمِت الباقي.</span>')
R('Every lead, call and client<br>in one place.','كل عميل محتمل ومكالمة وعميل<br>في مكان واحد.')
R('<span>Brand Victory · Growth Dashboard</span><em>Sample view</em>','<span><span class="ltr">Brand Victory</span> · لوحة النمو</span><em>عرض توضيحي</em>')
R('<div class="l">Leads this week</div>','<div class="l">عملاء محتملون هذا الأسبوع</div>')
R('<div class="l">Calls this week</div>','<div class="l">مكالمات هذا الأسبوع</div>')
R('<div class="l">Boost best post</div>','<div class="l">ترويج أفضل منشور</div>')
R('<h4>New <small','<h4>جديد <small'); R('<h4>Contacted <small','<h4>تم التواصل <small'); R('<h4>Booked <small','<h4>محجوز <small'); R('<h4>Client <small','<h4>عميل <small')
R('</u>Instagram</div>','</u>إنستغرام</div>',0); R('</u>Website</div>','</u>الموقع</div>',0); R('</u>WhatsApp</div>','</u>واتساب</div>',0); R('</u>Referral</div>','</u>إحالة</div>',0)
R('</u>New enquiry</div>','</u>استفسار جديد</div>')
R("['New enquiry','Replied ✓','Booked ✓','New client ✓']","['استفسار جديد','تم الرد ✓','تم الحجز ✓','عميل جديد ✓']")
R('<b></b>Lead in</div>','<b></b>استفسار</div>'); R('<b></b>AI replies</div>','<b></b>رد ذكي</div>'); R('<b></b>Call booked</div>','<b></b>حجز مكالمة</div>'); R('<b></b>Follow-up</div>','<b></b>متابعة</div>')
R("$('#k3').textContent=tg>.5?'ON':'OFF';","$('#k3').textContent=tg>.5?'مفعّل':'متوقف';")
R('>OFF</div><div class="tog"','>متوقف</div><div class="tog"')
# proof
R('<span class="ln"><span>Real experts. <span class="it ice">Real audiences.</span></span></span>','<span class="ln"><span>خبراء حقيقيون. <span class="it ice">وجمهور حقيقي.</span></span></span>')
R('<div class="l">Years building brands</div>','<div class="l">عاماً في بناء العلامات</div>')
R('<div class="l">Organic audience built</div>','<div class="l">متابع دون إعلانات مدفوعة</div>')
R('<div class="l">Markets</div>','<div class="l">أسواق</div>')
# testimonials (official Arabic translations from samtrabulsi.com)
R("<div class=\"q\">“I've seen a <em>significant increase</em> in brand recognition and customer engagement.”</div><div class=\"who\">Saly Zalzali</div><div class=\"role\">Women’s health and fitness expert</div>",
  '<div class="q">«لقد لاحظت <em>زيادة ملحوظة</em> في معرفة الناس بعلامتي وتفاعل العملاء معها.»</div><div class="who">سالي زلزلي</div><div class="role">خبيرة صحة المرأة واللياقة</div>')
R('<div class="q">“Sam has been instrumental in helping me grow my coaching business <em>from the ground up.</em>”</div><div class="who">Laila Hankir</div><div class="role">Coaching business owner</div>',
  '<div class="q">«كان لسام دور أساسي في مساعدتي على تنمية عملي في التدريب <em>من الصفر.</em>»</div><div class="who">ليلى حنقير</div><div class="role">صاحبة عمل في التدريب</div>')
open('scene_ar.html','w').write(s)
print('copy part ok')
