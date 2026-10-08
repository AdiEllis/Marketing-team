# מחקר: מקורות Skills ופרומפטים מקצועיים לכל סוכן

> נבדק ב-08.10.2026. הריפוזיטוריז נשלפו ונקראו ישירות, לא רק דרך אתרי דירוג. ספירות כוכבים משתנות בין מקורות, ולכן לא צוינו.
> **מדיניות:** לומדים מהמתודולוגיה וכותבים פרומפטים מקוריים בעברית. לא מעתיקים טקסט של Skill בלי רישיון מתאים.

| מקור | מה זה | רישיון | לאיזה סוכן | מה לוקחים |
|---|---|---|---|---|
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | אוסף Skills השיווק הנפוץ ביותר לסוכני AI (~50 Skills) | MIT ✅ | Strategist, Copywriter, Producer, Learning | `copywriting`, `copy-editing` (Seven Sweeps), `social` (Hook formulas), `ad-creative` (Angles ו-Iteration), `marketing-psychology`, `video` + `edit-anatomy`, `image` |
| [aicontentskills/ai-video-storyboard-skill](https://github.com/aicontentskills/ai-video-storyboard-skill) | Skill לבניית Storyboard רב-שוטי לווידאו AI | לא נמצא קובץ רישיון ⚠️ (לומדים מתודולוגיה בלבד) | Producer | Visual Theme Lock, Shot List, מבנים נרטיביים, אוצר מונחי צילום |
| [anthropics/skills](https://github.com/anthropics/skills) | Skills רשמיים של Anthropic | לפי תיקייה. `canvas-design`: Apache-2.0 ✅ | Creator (פוסטים), Producer | "Design Philosophy" לפני ביצוע, הדגשת Craftsmanship, `frontend-design` נגד מראה "AI גנרי" (לממשק) |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Framework פתוח: HTML/CSS/GSAP לווידאו MP4 דטרמיניסטי, "Built for agents" | Apache-2.0 ✅ | Creator | מנוע הרינדור המרכזי המומלץ (חלופה ל-Remotion, שמחייב רישיון לאוטומציה) |
| pexoai/pexo-skills, `videoagent-director` | Skill "במאי" שמציג טבלת שוטים לאישור לפני הפקה | לא נבדק | Producer, Orchestrator | עקרון "Shot table approval gate" |
| Meta research, [Decoding the Hook](https://arxiv.org/abs/2602.22299) | ניתוח 3 השניות הראשונות במודל מולטימודלי | מאמר | QA, Strategist | ה-Hook כיחידת הערכה נפרדת (ויזואל, אודיו, טקסט) |
| G-Eval / LLM-as-Judge ([Fora Soft guide](https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/eval-rigs-llm-as-judge-for-video)) | שיטת שיפוט מבוססת רובריקה | — | QA | שלבי הערכה לפני ציון, סולם קטן, כיול מול אדם |

## מקורות עיצוב (נוסף: סוכן Post Designer)
| מקור | רישיון | מה לוקחים |
|---|---|---|
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Apache-2.0 ✅ | Craft floor, רשימת Refuse (קרם עם Serif וקווים דקים; Eyebrow; מספור), אסטרטגיות צבע, "פנים מעולם הנושא", מצב Experience, Squint test |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | MIT ✅ | אילוצים שליליים, ניגוד טיפוגרפי, טיפול בצילום |
| anthropics/skills, `canvas-design` | Apache-2.0 ✅ | פילוסופיה ויזואלית לפני ביצוע, ‏90/10 ויזואל/טקסט, מלאכה |
| IBM Plex Sans Hebrew (Google Fonts) | OFL ✅ | פונט הפוסטים |

## כלים: ממצאי היתכנות ורישוי

| כלי | ממצא | השלכה |
|---|---|---|
| **Remotion** | חינמי לחברה עד 3 עובדים, אבל יש מסלול "Automators" לאוטומציה (‎$0.01 לרינדור, מינימום ‎$100 לחודש) | ❌ לא נבחר. HyperFrames (Apache-2.0) עדיף |
| **Wan 2.2** (Image-to-Video) | קוד פתוח Apache-2.0. גרסת 5B רצה על כרטיס צרכני (4090). על T4 חינמי ב-Colab: דקות רבות לקליפ, לא יציב לאוטומציה | אפשרי רק עם GPU. לא ב-PoC החינמי |
| **LTX-2.x** | רישיון חינמי מתחת ל-10M$ הכנסה שנתית, אבל המקורות סותרים | לבדוק את טקסט הרישיון לפני שימוש |
| **Veo (Google)** | ב-API **אין שכבה חינמית לווידאו**. מ-0.05$ לשנייה (Lite 720p) | ספק עתידי בתשלום |
| **Gemini API (טקסט וראייה)** | יש שכבה חינמית, אבל נתוני השכבה החינמית עשויים לשמש לשיפור מוצרים של Google | ⚠️ לא מתאים לתמונות מבתי לקוחות בלי הסכמה |
| **TTS עברית** | Phonikud/Piper עברית: הצ'קפוינטים **לא מסחריים (CC-NC)**. ElevenLabs חינם: בלי זכויות מסחריות. HebTTS: רישיון לא אומת | ❌ אין כרגע קריינות עברית חינמית, מסחרית ואיכותית מאומתת |
| **מוזיקה, Pixabay** | שימוש מסחרי בלי ייחוס, אבל בלי אחריות, ותיתכן תביעת Content ID | לתעד רישיון לכל רצועה, ולשקול הוספת מוזיקה באפליקציית אינסטגרם |
| **Depth Anything V2 Small** | הערכת עומק (Apache-2.0), רץ על CPU | Parallax 2.5D חינמי. לבדוק ב-PoC |

## מקורות נוספים
- [Best Open-Source Video Models (2026): Licenses Compared](https://fuser.studio/articles/best-open-source-video-models)
- [Wan2.2 TI2V-5B model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers)
- [Remotion license](https://www.remotion.dev/docs/pricing)
- [Phonikud paper](https://arxiv.org/abs/2506.12311), [Phonikud TTS checkpoints (CC-NC)](https://huggingface.co/Phonikud/phonikud-tts-checkpoints)
- [Veo pricing breakdown](https://www.atlascloud.ai/blog/tips/veo-3.1-ai-video-generator-free-or-paid), [Gemini free tier data use](https://prompts2products.substack.com/p/unpaid)
- [Pixabay music licensing caveats](https://musicgpt.com/blog/truly-safe-copyright-free-music/)
