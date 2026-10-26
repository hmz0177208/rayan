# خريطة روابط اللغات — موقع الريان للصرافة

- النطاق الأساسي: `https://rayyap.com` بدون `www`.
- السوق المستهدف: العراق فقط، بما يشمل إقليم كردستان العراق.
- أُنشئت صفحات فعلية بالإنجليزية تحت `/en/`، والفارسية تحت `/fa/`، والكردية العراقية السورانية تحت `/ku/`.
- بقيت المسارات العربية الحالية ثابتة. أضيفت روابط `hreflang` متبادلة فقط للصفحات التي لها مقابلات لغوية فعلية.
- كل نسخة مترجمة لها `canonical` ذاتي، و`lang` و`dir`، وبيانات عنوان/وصف وكلمات مستهدفة وسكيما محلية اللغة.
- زر تغيير اللغة موجود في أسفل الصفحات داخل قائمة منسدلة، وعلى صفحة تتبع الطلب يوجد داخل القائمة الجانبية. لا يوجد زر لتغيير اللغة في رأس الصفحة.
- لم يُنشر الموقع ولم يُختبر نطاقه أو الاستضافة الحية من هذه البيئة. الترجمة الكردية سورانية وتحتاج مراجعة لغوية بشرية قبل النشر.

| الصفحة | العربية الحالية | الإنجليزية | الفارسية | الكردية السورانية |
|---|---|---|---|---|
| الرئيسية | `https://rayyap.com/` | `https://rayyap.com/en/` | `https://rayyap.com/fa/` | `https://rayyap.com/ku/` |
| من نحن | `https://rayyap.com/about-us.html` | `https://rayyap.com/en/about-us.html` | `https://rayyap.com/fa/about-us.html` | `https://rayyap.com/ku/about-us.html` |
| الفروع وأماكن الاستلام | `https://rayyap.com/branches-locations.html` | `https://rayyap.com/en/branches-locations.html` | `https://rayyap.com/fa/branches-locations.html` | `https://rayyap.com/ku/branches-locations.html` |
| الأسئلة الشائعة | `https://rayyap.com/fuq.html` | `https://rayyap.com/en/faq.html` | `https://rayyap.com/fa/faq.html` | `https://rayyap.com/ku/faq.html` |
| سياسة الخصوصية | `https://rayyap.com/privacy-policy.html` | `https://rayyap.com/en/privacy-policy.html` | `https://rayyap.com/fa/privacy-policy.html` | `https://rayyap.com/ku/privacy-policy.html` |
| تتبع حالة الطلب | `https://rayyap.com/track.html` | `https://rayyap.com/en/track.html` | `https://rayyap.com/fa/track.html` | `https://rayyap.com/ku/track.html` |
| حجز الدولار للمسافرين | `https://rayyap.com/حجز-دولار-للمسافرين/index.html` | `https://rayyap.com/en/traveler-dollar-reservation/` | `https://rayyap.com/fa/traveler-dollar-reservation/` | `https://rayyap.com/ku/traveler-dollar-reservation/` |
| تأكيد/استكمال حجز الدولار | `https://rayyap.com/reservation/index.html` | `https://rayyap.com/en/reservation/` | `https://rayyap.com/fa/reservation/` | `https://rayyap.com/ku/reservation/` |
| تتبع حجز الدولار | `https://rayyap.com/reservation/track.html` | `https://rayyap.com/en/reservation/track.html` | `https://rayyap.com/fa/reservation/track.html` | `https://rayyap.com/ku/reservation/track.html` |
| خدمة ويسترن يونيون | `https://rayyap.com/westernunion/index.html` | `https://rayyap.com/en/western-union/` | `https://rayyap.com/fa/western-union/` | `https://rayyap.com/ku/western-union/` |
| تتبع حوالة ويسترن يونيون | `https://rayyap.com/westernunion/track.html` | `https://rayyap.com/en/western-union/track.html` | `https://rayyap.com/fa/western-union/track.html` | `https://rayyap.com/ku/western-union/track.html` |
| تتبع طلب تحويل | `https://rayyap.com/westernunion/track-order.html` | `https://rayyap.com/en/western-union/track-order.html` | `https://rayyap.com/fa/western-union/track-order.html` | `https://rayyap.com/ku/western-union/track-order.html` |
| تتبع تحويل برقم MTCN (الأصل الحالي إنجليزي) | لا توجد نسخة عربية مطابقة؛ أقرب صفحة معلومات عربية: `https://rayyap.com/westernunion/track.html` | `https://rayyap.com/westernunion/track-transfer.html` | `https://rayyap.com/fa/western-union/track-transfer.html` | `https://rayyap.com/ku/western-union/track-transfer.html` |


## إرشادات النشر والمراجعة

1. ارفع المجلدات والملفات كاملة مع الاحتفاظ بمجلد `wp-content`؛ الصفحات تستدعي أصولًا محلية منه.
2. اختبر الروابط والنماذج بعد النشر على الخادم الحقيقي؛ النسخة الثابتة قد لا تنفذ خدمات الخادم أو AJAX إن لم تكن نقاط التكامل متاحة.
3. أرسل `https://rayyap.com/sitemap.xml` إلى Google Search Console وBing Webmaster Tools بعد التأكد من نشر كل المسارات وعودة استجابات HTTP ناجحة.
4. راجع الترجمات الفارسية والسورانية، وخصوصًا المصطلحات المالية والنصوص القانونية وواجهات الحجز والدفع، بواسطة مراجع لغوي محلي قبل نشرها.
5. لا تعتمد على `meta keywords` وحده. الخطة التفصيلية للكلمات المفتاحية لكل صفحة ولغة موجودة في `SEO_KEYWORDS_MULTILINGUAL.md`.
6. مسار MTCN الأصلي `westernunion/track-transfer.html` هو واجهة إنجليزية قائمة؛ لم ننشئ نسخة إنجليزية ثانية حتى لا نصنع صفحة مكررة. أُنشئت نسختان مترجمتان بالفارسية والسورانية له.
