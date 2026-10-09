# מחקר מעמיק לכל תפקיד (אוקטובר 2026)

> **הטריגר:** משוב על פרויקט 3:
> - "נתקעת עם פורמט אחד".
> - "הכיתוב מתאמץ להסביר, עמוס במלל, בסרטון צריך יותר פאנץ'".
> - "המעברים משעממים ותקועים, אין פה משהו יצירתי, ירדנו ברמה".
> - "כל סוכן מומחה בתפקידו, תוצרים טרנדיים שתופסים את העין, יצירתיות ומגוון".
>
> **ארבעה מחקרים מקבילים** (רשת, אוקטובר 2026), על עריכת Reels, קופי קצר, עיצוב פוסטים, וקריאייטיב ו-QA. כאן התמצית שנכנסה לסוכנים, וקישורים למקורות.
>
> **אמינות:** חלק ממקורות 2025–2026 הם בלוגים של ספקי כלים. מספרים הם כיוון, לא חוק.

## למה "ירדנו ברמה" (אבחון)
1. **תיקון־יתר בקופי.** אחרי "מתאמץ מדי" נוסף כלל "לתאר מה רואים". הכרטיסים נהיו תוויות שחוזרות על התמונה (2–3 שורות לכרטיס).
2. **בחירה "בטוחה" בעריכה.** סימני UI בצילומים הובילו לפס טקסט קבוע ולדחיפות איטיות: 5 אירועים ויזואליים ב-18 שניות במקום 8–14.
3. **לא היה כלל מגוון מחייב.** אותה תבנית פוסט חזרה 3 פעמים.

סקילי הווידאו לא נדרסו (`git log`). הם פשוט לא דרשו יצירתיות ומגוון.

## 1. עריכת Reels מצילומי סטילס
**עקרונות:**
- **שנייה 0 כבר בתנועה** (באמצע Wipe, זום או טקסט). פותחים על הפריים הכי חזק, לא על לוגו ולא על Fade מהשחור.
- **8–14 אירועים ויזואליים** ב-15–25 שניות: שוט ממוצע של 1.5–3 שניות.
- **קצב מגוון:** מהר-מהר-**עצירה** (2–3 שניות על Hero)-מהר. קצב אחיד = "תקוע".
- **2–3 משפחות מעברים לכל סרטון**, לפי הסיפור. אם כל חיתוך אותו סוג, זה נראה כמו תבנית.
- **מעבר עם סיבה:** לפי קווי האדריכלות (פס, דלת, מדף, פאנל). זו הגרסה הפרימיום של "מעברים מגניבים".
- **לולאה:** הפריים האחרון מתחבר לראשון (צפייה חוזרת).
- **מגמת 2026:** מלאכה וטקסטורה מול ליטוש AI: גריד עריכתי, גרעיניות עדינה, צעדי פריימים. במינון.
- **אזורים בטוחים:** בלי טקסט בכ-150px העליונים, בכ-300px התחתונים ובכ-100px הימניים.

**קטלוג טכניקות** (פירוט היישום נמצא ב-`agents/creator.md`):

| קבוצה | טכניקות |
|---|---|
| מעברים לפי קווים וחיתוכים | 1. Wipe לאורך קו אדריכלי · 2. פסים/תריסים לפי חזיתות · 3. פיצול נגדי · 6. Match cut על צורה · 7. סליידר לפני/אחרי · 21. בלוק צבע |
| עומק וזום | 5. פורטל: זום דרך נישה · 14. פרלקסה 2.5D · 15. טקסט מאחורי המוצר |
| גריד וקולאז' | 4. גריד ובנטו ← Hero · 18. פילם · 19. מונטאז' מהיר |
| אור והבזק | 8. Light sweep · 9. דליפת אור · 10. שאטר |
| תנועה וקצב | 11. Scale-pop על ביט · 12. Speed ramp · 13. Whip עם blur · 16. סיבוב · 17. קיפול פאנל |
| טקסט וגרפיקה | 20. איריס לפי צורה · 22. טיפוגרפיה קינטית · 23. קווי מידה נמשכים |
| סיום וטקסטורה | 24. לולאה · 25. גרעיניות וצעדי פריימים |

**10 מבני Reels:**
1. סגור←פתוח
2. צלילה דרך פורטל
3. פרט-קודם (מסתורין)
4. בנייה עריכתית בבנטו
5. Hook טיפוגרפי
6. מונטאז' "Photo dump"
7. מסע Wipes לפי קווים
8. Light sweep אפל
9. לפני/אחרי (רק עם "לפני" אמיתי)
10. סדרה: "פרויקט אחד, 3 פרטים"

**מקורות:**
- Meta Reels tips (Social Media Today): https://www.socialmediatoday.com/news/meta-shares-reels-tips-for-marketers/806808/
- Meta על Hooks וגיוון קריאייטיב (Social Media Today): https://socialmediatoday.com/news/meta-shares-tips-on-reels-hooks-creative-diversification-in-ads-and-threa/808182
- מגמות מעברים (CapCut): https://www.capcut.com/create/video-transition-trends-viral-short-form-edits
- אסתטיקות עריכה 2026 (Opus): https://www.opus.pro/blog/editing-aesthetics-dominating-short-form-2026
- מגמות וידאו ומושן 2026: https://graphicdesignjunction.com/2026/01/video-and-motion-creative-trends-2026/
- מגמות מושן גרפיקס (Videobolt): https://blog.videobolt.net/post/top-motion-graphics-trends-2026
- אזורים בטוחים לטקסט: https://www.trymypost.com/blog/instagram-reels-safe-zones-text-placement-2026
- Clip-path grid (Codrops): https://tympanus.net/codrops/?p=93410
- Slice reveal (Codrops): https://tympanus.net/codrops/?p=72588
- לולאה (Later): https://later.com/social-media-glossary/loop/
- טקסט ו-occlusion ב-2.5D (CHI 2025): https://makeabilitylab.cs.washington.edu/media/publications/Su_Authoring25DDesignsWithDepthEstimation_CHI2025.pdf
- גיוון קריאייטיב ב-Andromeda (Jon Loomer): https://www.jonloomer.com/meta-andromeda-creative-diversification/
- **בנוסף:** הסקילים המקומיים `hyperframes-animation` (קטלוג מעברים, Rules, Blueprints) ו-`hyperframes-keyframes`.

## 2. קופי קצר ופאנץ'
- **התמונה כבר מתארת.** טקסט מוסיף משמעות, ניגוד, מספר, תזמון או תפנית. **מבחן ההשתקה:** מכסים את הטקסט ובודקים מה הפסדנו.
- **מספרים לכרטיסים:**
  - 1–4 מילים לכרטיס (6 לכל היותר).
  - 3–5 כרטיסים לכל סרטון, ו-20–35 מילים לכל היותר. אצלנו היעד 20.
  - 2–3 שוטים בלי טקסט.
- **יוקרה = ריסון:** "כל מילה היא קיר נושא". Bulthaup: "המטבח המושלם לא מושך תשומת לב לעצמו". Bottega: כמעט בלי קופי.
- **Apple:** פחות מ-12 מילים במשפט, מילה בודדת להדגשה, ארוך-קצר.
- **Sugarman:** "המגלשה": כל שורה קיימת כדי שתיקרא הבאה.
- **Ogilvy:** עובדה אחת במקום תארים, ועשרות כותרות כדי לבחור אחת.
- **ארגז כלים:** 18 טכניקות (ב-`agents/copywriter.md`).
- **Hooks בלי שאלה:** פתיחה על הרגע הטוב, פער סקרנות, הצהרה, מספר, ניגוד, פרט-קודם.
- **כיתובים:**
  - 125 התווים הראשונים כוללים Hook ומילת חיפוש.
  - 3–5 האשטגים.
  - רילס: קצר, לחשיפה. קרוסלה: ארוך, לשמירות.

**מקורות:**
- לכתוב כמו Apple (Neil Patel): https://neilpatel.com/blog/write-copy-like-apple/
- לכתוב כמו Apple (Enchanting Marketing): https://www.enchantingmarketing.com/write-like-apple/
- Joseph Sugarman: https://larslofgren.com/joseph-sugarman/
- מודעת Rolls-Royce של Ogilvy: https://swiped.co/rolls-royce-ad-by-david-ogilvy
- Predatory Thinking (Dave Trott): https://www.procopywriters.co.uk/2013/08/predatory-thinking-by-dave-trott/
- Hey Whipple (Luke Sullivan): https://www.shortform.com/pdf/hey-whipple-squeeze-this-pdf-luke-sullivan
- יוקרה שקטה: https://translated.com/resources/quiet-luxury-brands-translation-communicating-less
- קופי ליוקרה (Appnova): https://www.appnova.com/8-copywriting-essentials-to-turn-luxury-brand-browsers-into-buyers/
- כמות מילים בווידאו (Biteable): https://biteable.com/blog/video-word-count/
- Reels מול קרוסלות 2026: https://contentdrips.com/blog/2026/06/instagram-reels-vs-carousels-2026-guide/
- האשטגים ב-2026: https://corkboardconcepts.com/marketing-resources/blog/are-hashtags-still-relevant-in-2026/
- IKEA, גרנד פרי Epica: https://www.epica-awards.com/news/print-grand-prix-try-moves-us-one-line-ikea

## 3. עיצוב פוסטים וקרוסלות
- **פלטפורמה:**
  - 1080×1350. הגריד בפרופיל חותך ל-3:4.
  - שקף 2 = "שער שני".
  - 3–5 שקפים לתצוגה, 7–10 לתוכן מלמד.
- **18 ארכיטיפים** (ב-`agents/post-designer.md`): Hero, יוקרה שקטה, מגזין, תוויות חומר, מפוצל, פנורמה, רצף זום, "3 פרטים", Spec, פלטה, מסגרת, פסיפס, טיפוגרפי, פילם, "איך זה עובד", גזירה, זכוכית מגדלת, סיפור.
- **2026:**
  - חזרת הסריף העריכתי.
  - ניגוד סקאלה (ענק או זעיר, לא בינוני).
  - פלטה טונלית מהצילום עם מבטא אחד.
  - גרעיניות עדינה, פינות חדות וקווים דקים.
- **גיוון:**
  - DNA קבוע (גרייד, 2 גופנים, פלטה, לוגו, CTA); הפריסה, הסקאלה והטון משתנים.
  - לא אותו ארכיטיפ פעמיים ברצף, ולכל היותר פעמיים ב-9 פוסטים.
  - מחליפים רועש ושקט, וכהה ובהיר.

**מקורות:**
- אסטרטגיית קרוסלות 2026 (True Future Media): https://www.truefuturemedia.com/articles/instagram-carousel-strategy-2026
- קרוסלות (Metricool): https://metricool.com/instagram-carousels/
- שימושים יצירתיים בקרוסלות (Sked Social): https://skedsocial.com/blog/creative-ways-to-use-instagram-carousels-in-2025
- הגריד האנכי החדש (Planoly): https://planoly.com/blog/guide-to-instagrams-new-vertical-grid
- ביטול חובת החיתוך (MobileSyrup): https://mobilesyrup.com/2025/05/29/instagram-no-longer-requires-you-to-crop-pictures/
- רעיונות לפריסת גריד (Statusbrew): https://statusbrew.com/learn/instagram-grid-layout-ideas/
- קרוסלה רציפה (Krumzi): https://www.krumzi.com/blog/seamless-instagram-carousel
- שיווק מותגי יוקרה ברשתות (Sprout Social): https://sproutsocial.com/insights/luxury-brand-social-media-marketing-uk/
- Quiet design (Icon Eye): https://www.iconeye.com/sponsored-content/quiet-design-how-luxury-brands-are-redefining-power-through-restraint
- מצב העיצוב (DesignRush): https://www.designrush.com/trends/state-of-design
- מגמות עיצוב גרפי (Gelato): https://www.gelato.com/blog/graphic-design-trends
- ריסון בפיד של Aman: https://en.10minhotel.com/?p=163412

## 4. קריאייטיב (Strategist) ו-QA
- **תהליך רעיונות:**
  - James Webb Young: איסוף, עיכול, דגירה, הארה, עיצוב.
  - Dave Trott: מבט זר, "Upstream" (הבעיה של הצופה).
  - Burnett: "הדרמה הפנימית", "רק הפרויקט הזה ___".
  - שבירת שגרה: SCAMPER, PO של de Bono, מילה אקראית, החלפת נקודת מבט.
  - Sutherland: "ההפך מרעיון טוב".
  - **מסנן אמת:** ASA ו-NAD. לפני/אחרי רק מאותה זווית, ומטאפורה רק בטיפוגרפיה ובתנועה.
- **18 מכשירים** (ב-`agents/creative-strategist.md`).
- **גיוון:**
  - נכסים מבחינים קבועים: Byron Sharp, ו-"Fluent device" של System1.
  - הקונספט מתחלף. Meta Andromeda מקבצת יחד מודעות דומות.
  - עמודי תוכן, וסדרות במינון של בערך פוסט אחד מכל 3.
- **QA:** כרטיס ניקוד 0–2 על Attract, Brand, Connect, Distinct, Truth/Direct.
  - יוצאים לדרך מ-16/20, ובלי 0 בקריטריונים החוסמים.
  - **מבחן "משעמם":** דגימה כל 2 שניות. שתי דגימות זהות ברצף = משעמם.

**מקורות:**
- Google ABCDs: https://business.google.com/us/think/future-of-marketing/creative-best-practices-youtube-ads/
- Google ABCDs (PDF): https://services.google.com/fh/files/misc/core_abcds_of_effective_creative.pdf
- TikTok creative best practices: https://ads.tiktok.com/help/article/creative-best-practices
- Meta Andromeda (Jon Loomer): https://www.jonloomer.com/meta-andromeda/
- James Webb Young: https://daverothacker.com/webapp/p/309/a-technique-for-producing-ideas
- Dave Trott: https://www.alexmurrell.co.uk/summaries/dave-trott-predatory-thinking
- Rory Sutherland: https://www.alexmurrell.co.uk/summaries/rory-sutherland-alchemy
- SCAMPER (IMD): https://imd.org/blog/innovation/scamper-method-design-thinking/
- Fluent devices (GreenBook): https://www.greenbook.org/insights/market-research-industry/the-power-of-fluent-devices
- זוכי Cannes Lions 2025 (Contagious): https://www.contagious.com/en/article/news-and-views/cannes-lions-2025-the-grand-prix-winning-campaigns
- תמונות לפני/אחרי (ASA): https://www.asa.org.uk/advice-online/before-and-after-photos.html
- Benchmarks של אינסטגרם 2025 (Socialinsider): https://www.socialinsider.io/data-geeks/instagram_benchmarks_2025.pdf
- מדדי ביצועי קריאייטיב (Motion): https://motionapp.com/blog/key-creative-performance-metrics

> **תיקון אחרי משוב:** המלצות מהמחקר על "Folio / מספור 1/5" ו"חץ החלקה" **נפסלו אצלנו.** הן נראות כמו ממשק אינסטגרם.
