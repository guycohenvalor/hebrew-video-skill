---
name: hebrew-video
description: Produce high-conversion Hebrew marketing, social, and product videos in 16:9 landscape (desktop demo/client walkthrough), 9:16 vertical (Instagram Reels, YouTube Shorts, TikTok), and automated Screen Studio browser recordings — all rendered at a broadcast-grade 60 FPS standard. Features real Image-to-Video generative motion, cloned Hebrew voiceover (ElevenLabs eleven_v3, voice IVC10), centisecond-accurate Whisper RTL captions with dynamic badges, and Screen Studio browser automation with cubic Bezier cursor, click ripples, keystroke HUD, and dynamic camera zoom/pan. Rendered via headless Chrome overlays, Playwright, and ffmpeg (CRF 17, 60 FPS). Use for any "סרטון", "וידאו", "רילס", "שורטס", "קריינות", "כתוביות", "דיבוב", "הקלטת מסך", "דמו דפדפן", "Screen Studio", client demo, or automated video studio. Never use HyperFrames on this machine.
---

# Hebrew Video Production Pipeline (60 FPS Broadcast Standard)

Everything runs from a **project folder** that holds configuration, `assets/`, `overlays/` and `out/`. Rendered with headless Chrome, Playwright, and ffmpeg compositing at 60 FPS.

## Hard Rules & Production Safeguards

1. **Never run `npx hyperframes …` on this PC:** HyperFrames commands wiped directories. This independent Chrome + ffmpeg pipeline replaces it completely.
2. **Platform Duration Budget (< 60.00s for Shorts/Reels):** Vertical videos must strictly remain below 60.00 seconds (ideal target: 50.0s to 58.5s). Any duration at or over 60.00s breaks short-form categorization and video loops.
3. **Pronunciation Golden Rule (Zero Ambiguity):**
   - Hebrew words with vowel ambiguity (e.g. "ערכה" which TTS mispronounces as "ARAKA" or with penultimate English stress "ÉR-ka") must **not** be fought with endless acoustic hacks.
   - **Immediately substitute ambiguous words with clean, unambiguous synonyms** (e.g. replace "ערכה" with "חבילה").
   - Technical loanwords: ensure explicit hard consonants (e.g. "טלפרומפטר" with dagesh in Pe, not "telefrompter").
   - **Zero vocal groans or snore simulations:** Never attempt to generate snore sounds, sighs or grunts ("אה אה אה") via TTS. They sound distorted and bizarre. Keep narration articulate and pair with subtle background music and clean SFX.
4. **Voice Engine:** ElevenLabs `eleven_v3` only. Voice **IVC10 = `ND8JTbPy2RGiXF2rpt6p`** ("Guy HE IVC 10min"), settings `stability 0.5, similarity 0.75`, no style/speed.
5. **Verbatim Subtitle Synchronization (Whisper Alignment):**
   - Captions must match the spoken words 100% verbatim. Dropping words (like "ללכת", "מהחיים", "בינה מלאכותית", "ממני") breaks synchronization.
   - Extract timestamps using `faster-whisper` (`word_timestamps=True`) directly on the final mixed/spliced audio.
6. **Keys and Config:** Keys live in `~/.config/valor-video/.env` (`ELEVENLABS_API_KEY=`) or environment variables. Never commit keys into project repos.
7. **Broadcast 60 FPS Standard (איסור מוחלט על קפיצות וריצוד פריימים):**
   - כל הפקות הווידאו בסקיל (16:9 Landscape, 9:16 Reels, Loops, ו-Screen Studio) מקודדות בתקן שידור של **60.0 FPS מלא** (`-r 60`, `-filter:v fps=60`, `-c:v libx264 -preset slow/medium -crf 17-18 -pix_fmt yuv420p`).
   - לעולם אין לרנדר ב-24/25/30 FPS שגורמים לתנועת עכבר מקוטעת, ריצוד טקסט וקרטועים במעברי מצלמה.

---

## Mode 1: 9:16 Vertical Reels / Shorts (Mobile Social)

### 1. Typography & Dynamic Badges
- **Font:** **Heebo Black** (`font-weight: 900`, -0.5px letter-spacing). Never use serif or standard desktop fonts.
- **Chunk Density:** 2 to 4 words per caption box. Fast, punchy and readable on mobile.
- **Badge Styling:**
  - Plain words: White `#ffffff` with heavy black stroke (`-webkit-text-stroke: 10px #000; paint-order: stroke fill;`) and deep drop shadow.
  - Active highlight badge: Rounded pill (`border-radius: 16px`, padding `8px 24px`), colored in vibrant yellow (`#facc15`) or electric cyan (`#38bdf8`) with black text (`#000000`).
  - Badge timing: Pops exactly on the start millisecond of the spoken keyword.
- **Vertical Safe Zones:**
  - Standard talking head / chest placement: `bottom: 810px`.
  - Cleared zone when lower third has prominent subjects (pets, desks, devices): `bottom: 1020px`.

### 2. Visual Animation & Camera Flow
- Divide video into 5 to 6 distinct visual scenes (7 to 12 seconds each).
- When animating static illustrations, avoid aggressive AI morphing that distorts human faces or eyes.
- Special visual cues (e.g. eye sparkle flare, graphic badges) must be placed at exact cue times.

### 3. Audio Mastering
- Speech normalized to `-14 LUFS` (`loudnorm=I=-14:TP=-1.5:LRA=11`).
- Royalty-free background music ducked to `volume=0.08` with a gentle `lowpass=f=4500` filter so narration remains crystal clear.
- Sound effects (whoosh, ping, sparkle, chime) mixed with millisecond precision via ffmpeg `adelay`.

---

## Mode 2: 16:9 Landscape Product & Client Demos (B2B Walkthrough)

### 1. Workflow
1. `mkdir C:\Users\Valor\Videos\<Project>\assets` and copy in: screen recording, `valor-logo-white.png`, `robot.png`.
2. Copy `templates/project.json` and edit: narration lines, scene list, chip labels, card texts, blur boxes.
3. Clean footage: `python ~/.claude/skills/hebrew-video/scripts/clean_footage.py` (crop browser chrome + time-boxed `boxblur`).
4. Voice: `python ~/.claude/skills/hebrew-video/scripts/vo.py` -> `assets/vo/vo<N>.wav` + `vo.json`.
5. Pronunciation QA: `python ~/.claude/skills/hebrew-video/scripts/qa_vo.py`.
6. Render: `python ~/.claude/skills/hebrew-video/scripts/render.py` -> `out/<name>.mp4`.

### 2. Captions & Capability Chips
- Spoken text and on-screen text differ on purpose: `display` in `project.json` maps spoken -> shown (digits, clock format, product terms).
- One caption = one single line (<= 50 chars at 54px), positioned at `bottom: 110px`.
- Benefit-phrased top-right chips appear 0.3s into a scene and stay **exactly 4 seconds**.
- **Fixed spellings (Guy's rulings):** speak **"וָואלוֹר"** -> show `Valor`; speak **"UI Path"** (two English words, capital UI, space) -> show `UiPath`. Never write `Valor` or `UiPath` as one word in spoken text.
- Loanwords: write in Latin script inside Hebrew line ("בקבצי ה-log", `tolerance`, `job`).
- Words to avoid/fix: say "מיום שני" not "משני", "התפספס" not "פוספס", "פעלו" not "רצו", "לחפש" not "לחפור".

---

## Mode 3: Silent & "Punch" Conference Loops

### 1. Standard Silent Loop (`render_loop.py`)
- Renders no-narration loop from `project.json -> timeline` with big 96px titles (3-5 words per shot) and contact QR card.

### 2. High-Impact "Punch" Loops (`render_punch_loop.py`)
- **Visuals:** Minimalist, bold poster typography (140px-210px), big glowing numbers, dark cyber-grid.
- **Music:** Upbeat, driving, positive corporate tech / electro-pop (128-138 BPM, e.g. `Presenterator`, `Shiny Tech`), continuous at ~ -13 LUFS.
- **Strict Audio Bans (Management ruling):**
  - NO artificial explosion / sub-bass "boom" SFX on transitions (`sub_landing.wav`).
  - NO aggressive sidechain ducking pump on video cuts.
  - NO dark, scary, dissonant, horror or noisy industrial tracks (`REACTOR`).
  - NO quiet elevator/piano music (`bed1` at 0.35 gain).

---

## Mode 4: Social Post to Animated Reel (פוסט לסרטון ריל מונפש עם דיבוב)

מודל זה ממיר פוסט קיים (תמונה וטקסט מלינקדאין, פייסבוק או אינסטגרם) לסרטון רילס אנכי (9:16) מרהיב, הכולל דיבוב משובט, אנימציית וידאו אמיתית (Image-to-Video), כתוביות קינטיות ומאסטרינג אודיו מלא.

### 1. חוק ברזל: אנימציה גנרטיבית אמיתית (איסור על תמונות סטטיות עם פאן/זום בלבד)
- **הלקח המרכזי מסרטון הסטודיו:** תמונה סטטית עם תנועות פאן/זום עדינות (Ken-Burns) מרגישה כמו מצגת שקופיות מיושנת. הצופה מזהה תוך שנייה שמדובר בתמונה קפואה והמעורבות צונחת.
- **חובה לייצר אנימציית וידאו אמיתית (Real Image-to-Video Motion):**
  - גזירת קרופים אנכיים (9:16) ברזולוציה גבוהה מתוך תמונת הפוסט הראשית בהתאם לנושא של כל סצנה.
  - הנפשת כל סצנה באמצעות מודלי וידאו גנרטיביים מובילים (Kling AI, MiniMax Hailuo, Runway Gen-3 Alpha, Luma Dream Machine, Sora, Wan 2.1).
  - פרומפטי תנועה ייעודיים לכל סצנה:
    - *דמות אנושית/יוצר*: נשימה טבעית (heaving chest), מצמוצי עיניים, חיוך עדין, תנועות ראש קלות, שינויי תאורת סביבה.
    - *סביבת עבודה ורובוט*: זרוע מכנית שמקלידה על מקלדת פיזית, מסכים מרצדים עם קוד שרץ וגלי סאונד מונפשים, חלקיקי אבק באלומת אור.
    - *ממשקים ומסכים*: חלונות צפים שמתעדכנים, גרפים קופצים, אלמנטים גרפיים מונפשים.
- **טכניקת לופ פינג-פונג (Ping-Pong Loop) להארכת סצנה:**
  - מודלי I2V מייצרים בדרך כלל 4 עד 5 שניות וידאו, בעוד ביט בתסריט נמשך 7 עד 12 שניות.
  - משתמשים בלופ פינג-פונג רציף (`cycle if cycle < n_frames else 2*(n_frames - 1) - cycle`) כדי שהסצנה תישאר בתנועה חיה וזורמת לכל אורך הקריינות, ללא קפיצות וללא פריים קפוא.

### 2. שלד תסריט 6 הביטים (The 6-Beat Narrative Framework)
עיבוד טקסט הפוסט לתסריט וידאו אנכי קצבי באורך 50 עד 58 שניות (< 60.00 שניות בסך הכל):
1. **ביט 1 (00:00 - 00:08) | הוק והתוצאה המושלמת (Hook & Dream):**
   - תוצאה מעוררת השראה או היפוך ציפיות (לדוגמה: "חזרתי ליקיצה טבעית ולשבע שעות שינה, והכל בזכות סוכן בינה מלאכותית שמייצר לי סרטונים וחוסך לי את הטרחה.").
2. **ביט 2 (00:08 - 00:18) | הכאב והתסכול מהעבר (The Relatable Struggle):**
   - המחשת נקודת השפל שהקהל מזדהה איתה (לדוגמה: "פעם, כל סרטון שאב לי שעתיים מהחיים. הייתי מצלם שישה טייקים, מדבר למצלמה חצי שעה ברצף, נותן את הופעת חיי, ורק בסוף מגלה שהמיקרופון היה כבוי !").
3. **ביט 3 (00:18 - 00:29) | נקודת המפנה וההחלטה (The Turning Point / Breakthrough):**
   - הרגע שבו נמאס והוחלט לפעול (לדוגמה: "במקום ללכת לישון כמו בן אדם, ישבתי מול תוכנת העריכה. סנכרון כתוביות, חיתוך סצנות. העריכה תמיד הייתה הקיר, אז שברתי אותו ובניתי לעצמי סטודיו אוטומטי !").
4. **ביט 4 (00:29 - 00:38) | מנוע האוטומציה (The Secret Engine):**
   - החיבור של היכולות לחבילה אחת שעובדת בפקודה בודדת (לדוגמה: "לקחתי את הסקיל, חיברתי לו עוד כמה יכולות, וארזתי הכל לחבילה אחת. היום, כל ריל שאתם רואים ממני יוצא בפקודה אחת !").
5. **ביט 5 (00:38 - 00:50) | הוכחה והצגת מנגנון (Live Proof & Features):**
   - הצגת היכולות ברצף מהיר: טלפרומפטר בדפדפן, סלפי אחד, כתוביות מילה במילה, חיתוך שקט אוטומטי, דיבוב משובט ב-ElevenLabs.
6. **ביט 6 (00:50 - 00:58) | שורת מחץ והנעה חברתית לפעולה (The Social CTA):**
   - יצירת שיחה בתגובות (לדוגמה: "זה נשמע מקצועי ומחזיר לי שעתיים של שפיות ביום ! רוצים את החבילה המלאה ? כתבו סטודיו בתגובות ואשלח לכם הכל. מקסימום תמשיכו לצלם שישה טייקים על מיוט !").

### 3. דיבוב והקפדה על הגייה נקייה
- **שיבוט קול:** שימוש בקול המשובט של גיא ב-ElevenLabs (`ND8JTbPy2RGiXF2rpt6p`) במודל `eleven_v3`.
- **כלל ההחלפה המיידית למילים עמומות:** מילים ש-TTS מתקשה להגות או מדגיש לא נכון (כמו "ערכה" שנשמעת כמו ARAKA או מלעיל) מוחלפות מיד במילה נרדפת חלקה (כמו "חבילה").
- **איסור על קולות גניחה/נחירה ב-TTS:** לעולם לא מנסים לייצר נחירות או אנחות ("אה אה אה") דרך מנוע הדיבוב. הטקסט נשאר רהוט, והאווירה נבנית באמצעות מוזיקה ואפקטי סאונד.
- **סנכרון מוחלט ב-Whisper:** חילוץ זמני מילים באמצעות `faster-whisper` (`word_timestamps=True`) ישירות על קובץ האודיו המוגמר.

### 4. כתוביות קינטיות, תגיות פיל ואפקטים ויזואליים
- פונט **Heebo Black** (`font-weight: 900`, -0.5px letter-spacing), עם קו מתאר שחור עבה וצל עמוק.
- צפיפות של 2 עד 4 מילים לתיבה.
- תגיות פיל (Dynamic Highlight Pills) בצבע צהוב זרחני (`#facc15`) או טורקיז חשמלי (`#38bdf8`) עם טקסט שחור, הקופצות בדיוק במילישנייה שבה מילת המפתח נאמרת.
- תגיות סטטוס עליונות (Scene Chips) להצגת ההקשר של הסצנה (`<span class="chip-tag">STUDIO AI</span>`, `PAIN`, `BREAKTHROUGH`, `GET IT`).
- אפקטים ויזואליים מתוזמנים: ניצוץ יהלום (`draw_diamond_sparkle`) ברגעי קסם, הבזק אדום כשמוזכר מיקרופון כבוי, ואפקטים קוליים מותאמים (whoosh, sparkle chime, click).

### 5. מאסטרינג אודיו ומוזיקה
- דיבוב מנורמל ל- `-14 LUFS` (`loudnorm=I=-14:TP=-1.5:LRA=11`).
- מוזיקת רקע אופטימית/הירואית מונמכת ל- `volume=0.08` עם פילטר `lowpass=f=4500` כדי לשמור על בהירות הדיבור.
- שילוב אפקטים קוליים מדויקים במילישניות של חיתוכי הסצנות ותגיות ההדגשה.

### 6. מבנה תיקיית פרויקט לסרטון מפוסט
```
projects/<post_name>/
├── post_source/
│   ├── post_text.txt
│   └── hero_image.jpg
├── ai_video/
│   ├── crop_s1.jpg -> anim_scene1.mp4 (Kling / MiniMax I2V)
│   ├── crop_s2.jpg -> anim_scene2.mp4
│   └── ...
├── tts/
│   ├── scene1.wav + scene1.json (ElevenLabs timestamps)
│   └── ...
├── overlays/
│   ├── vbadge_scene1.png
│   └── ...
└── out/
    └── <post_name>_reel.mp4
```

---

## Mode 5: Screen Studio & Automated Browser Recording (הקלטות מסך דמו ברמת סטודיו ב-60 FPS)

מודל זה מפיק הקלטות וידאו אוטומטיות, חיות ומלוטשות ברמת **Screen Studio** ו-**Cursor Benchmark**, עבור הדגמת כלים, מוצרי ווב ומערכות ארגוניות. הסרטון מציג חוויית משתמש אינטראקטיבית חלקה וזורמת, ללא צילומי מסך מקוטעים, תוך שימוש בתנועת מצלמה דינמית (זום ופאן), עכבר וירטואלי מונפש, חיווי לחיצות טקטילי, תגיות קיצורי מקלדת (HUD), וקידוד שידור ב-**60 FPS**.

### 1. מעטפת הסטודיו (Studio Shell Architecture)
- **תבנית:** `templates/studio_recorder.html` מרכזת את כל האלמנטים של סביבת העבודה (Desktop Environment) ברזולוציית בסיס 1920x1200 (או 1920x1080).
- **סביבת עבודה וטפט (Desktop & Wallpaper):**
  - רקע סטודיו עמוק (גרדיאנט יוקרתי כהה כברירת מחדל, או קובץ `wallpaper.jpg` עם טשטוש עדין ו-Vignette).
  - סרגל תפריט עליון שקוף למחצה (`#top-bar`) ושורת אפליקציות תחתונה (`#os-dock`).
- **מסגרת דפדפן פרימיום (Chrome / macOS Window Shell):**
  - חלון מרכזי מעוגל (`border-radius: 12px`, צל עמוק `box-shadow: 0 40px 100px rgba(0,0,0,0.65)` ומסגרת 1px זוהרת בעדינות).
  - פקדי חלון macOS (נקודות אדום, צהוב, ירוק).
  - שורת טאבים פעילה עם אייקון, כותרת מותאמת אישית וכפתור סגירה.
  - סרגל כתובות (Omnibox) הכולל כפתורי ניווט, מנעול SSL, וכתובת URL נקייה בפונט מונוספייס.
  - מסגרת האפליקציה: אלמנט `iframe` פנימי (`#app-frame`) שמארח את האפליקציה החיה.

### 2. עכבר וירטואלי מדויק ללא הסטה (Coordinate-Invariant Virtual Cursor)
- **חוק ברזל: העכבר ממוקם בתוך `#desktop` ולא בתוך ה-iframe:**
  - כאשר המצלמה מבצעת זום ופאן על `#desktop`, העכבר הווירטואלי זז, גדל ומתקרב יחד עם התוכן בדיוק מתמטי של 100%, ללא כל בריחת קואורדינטות (Zero Coordinate Drift).
- **נוסחת המרת קואורדינטות מאלמנט ב-iframe לשולחן העבודה:**
  ```python
  desktop_x = 70 + iframe_el_x
  desktop_y = 130 + iframe_el_y
  ```
- **אינטרפולציית תנועה חלקה (Ease-Out Cubic):**
  - העכבר נע באמצעות פונקציית מעבר Bezier המדמה תנועת יד טבעית עם האצה ראשונית והאטה עדינה לפני עצירה:
    ```javascript
    const easeT = 1 - Math.pow(1 - t, 3);
    currentCursorX = startX + (targetX - startX) * easeT;
    currentCursorY = startY + (targetY - startY) * easeT;
    ```
  - משך תנועה אופטימלי: 700ms עד 900ms בין רכיבים במסך.

### 3. חיווי לחיצות טקטילי ו-HUD מקלדת צף (Tactile Ripples & Keystroke HUD)
- **אפקט גל לחיצה (Click Ripple):**
  - בכל לחיצה על כפתור או שדה, מופעלת פונקציית `window.studioClick()`.
  - מיוצר אלמנט `.click-ripple` עם טבעת זוהרת (`border: 2.5px solid rgba(56, 189, 248, 0.95)`), המתרחבת מ-scale 0.2 ל-scale 3.2 ונמוגה תוך 650ms.
- **תגית HUD צפה לקיצורי מקלדת (`#key-hud`):**
  - בעת שימוש בקיצורים (כגון סימון הכל `^A`, מחיקה, או פעולות מערכת), מופעלת `window.studioShowHud('^A')`.
  - תגית כהה מעוגלת ויוקרתית (Dark Glassmorphism) צפה בתחתית המסך ומציגה לצופה את הפקודה המדויקת.

### 4. בקרת מצלמה דינמית ומקצב נשימה (Dynamic Camera Breathing Cadence)
- **חוק ברזל: שילוב מתוזמן בין תקריב (Focus) למבט רחב (Overview):**
  - טעות נפוצה: הישארות ממושכת בזום של 1.25x-1.35x מעלימה את שולי החלון, הטפט של שולחן העבודה והדוק, ומאבדת את חוויית ה-Screen Studio הייחודית.
  - **מקצב הנשימה התקני שנלמד מ-Cursor Benchmark:**
    1. **פתיחה רחבה (00s-03s):** מבט רחב 1.0x המציג את סביבת שולחן העבודה, הטפט, החלון הצף והדוק במלוא הדרם.
    2. **תקריב לפעולה (Focus):** זום חלק ל-1.26x-1.28x בדיוק בזמן הקלדה ממוקדת בשדה, כדי לאפשר קריאה נוחה וחדה של הטקסט.
    3. **חזרה למבט רחב (Overview):** מיד עם סיום ההקלדה, המצלמה חוזרת בצורה חלקה ל-1.0x כדי להציג את התעדכנות התוצאות בהקשר הרחב של המערכת.
    4. **זום עדין לבחינת טבלאות נתונים:** 1.08x בלבד, המאפשר קריאת שורות ועמודות תוך שמירה על שולי החלון והטפט של שולחן העבודה בתמונה.
    5. **גרנד פינאלה:** סיום יציב ב-1.0x המציג את המערכת הגמורה עם כל הנתונים, המספרים וכרטיסי החישוב.

### 5. ארכיטקטורת רינדור 60 FPS אמיתית (True 60 FPS Compositor Stepping)
- **מדוע הקלטת המסך הרגילה של Playwright (`record_video_dir`) נכשלה:**
  - מנגנון ה-Screencast הפנימי של Chromium מוגבל בקוד המקור C++ ל-25 FPS בלבד (`options.kDefaultFramesPerSecond = 25`).
  - שימוש ב-FFmpeg `-filter:v fps=60` על מקור של 25 FPS רק משכפל פריימים (Duplicate Frames: A, A, B, B, B...), והעין רואה סרטון מקרטע ב-25-30 FPS.
  - שימוש באינטרפולציית תנועה (`minterpolate` או `framerate`) מייצר טשטוש מריחה כפול (Ghosting / Double Cursor) בלתי נסבל.
- **הפתרון המנצח: שליטה בקומפוזיטור דרך Chrome DevTools Protocol (`HeadlessExperimental.beginFrame`):**
  - Chromium מופעל במצב Headless עם הדגלים:
    `--enable-begin-frame-control --run-all-compositor-stages-before-draw --disable-new-content-rendering-timeout --no-sandbox`.
  - נפתחת סשן CDP (`context.new_cdp_session(page)`) עם הפעלת `HeadlessExperimental.enable`.
  - מתבצעת לולאת פריימים דטרמיניסטית ב-Python (`3600` פריימים עבור 60 שניות, `dt = 16,666.67 µs`):
    1. קידום מצב ה-DOM והאנימציות ב-JS: `page.evaluate(f"window.studioSeek({t_sec:.5f})")`.
    2. שליחת פקודת ציור ישירה לקומפוזיטור:
       ```python
       res = client.send('HeadlessExperimental.beginFrame', {
           'frameTimeTicks': 1000000 + frame_idx * 16666.666667,
           'interval': 16666.666667,
           'screenshot': {'format': 'jpeg', 'quality': 88}
       })
       ```
    3. הזרמת בייטי התמונה ישירות אל `stdin` של FFmpeg בצינור `image2pipe` ללא שמירת קבצים זמניים בדיסק:
       ```python
       cmd = [
           'ffmpeg', '-y',
           '-f', 'image2pipe',
           '-vcodec', 'mjpeg',
           '-r', '60',
           '-i', '-',
           '-c:v', 'libx264',
           '-preset', 'fast',
           '-crf', '17',
           '-pix_fmt', 'yuv420p',
           output_mp4
       ]
       ffmpeg_proc.stdin.write(base64.b64decode(res['screenshotData']))
       ```
  - **תוצאות מדידה מוכחות (Verified Metrics):**
    - **60.0 FPS מדויק** (3600 פריימים עבור 60.00 שניות).
    - **0 Duplicate Frames** בזמן תנועה (כל פריים מכיל דלתא פיקסלית ייחודית וחדה).
    - **0 Ghosting / Motion Blur** (קצוות עכבר חדים ברמת הפיקסל הבודד).
    - מהירות רינדור: 20-30 FPS (סרטון של דקה מתרנדר בפחות מ-3 דקות).

---

## Project Execution Checklist

### מסלול א': סרטון ריל מונפש מפוסט (9:16 Vertical Reel)
1. **פוסט לתסריט ואימות הגייה:**
   - חילוץ הטקסט והתמונה המקורית מהפוסט.
   - חלוקה ל-6 ביטים נרטיביים ממוקדים (< 60.00 שניות).
   - בדיקת מילים עמומות והחלפתן במילים נרדפות חלקות (לדוגמה: "חבילה" במקום "ערכה").
2. **אנימציית וידאו גנרטיבית (Image-to-Video):**
   - גזירת קרופים אנכיים (9:16) ברזולוציה גבוהה מתוך התמונה הראשית של הפוסט.
   - יצירת אנימציית וידאו חיה לכל קרופ במודל I2V (Kling, MiniMax, Runway, Luma) עם פרומפטי תנועה מותאמים.
   - החלת לופ פינג-פונג לשמירה על תנועה רציפה לאורך כל משך הקריינות של הסצנה.
3. **הפקת דיבוב וסנכרון Whisper:**
   - הרצת `eleven_v3` עם הקול של גיא (`ND8JTbPy2RGiXF2rpt6p`). שמירה כ-WAV סטריאו 48kHz.
   - הרצת `faster-whisper` עם `word_timestamps=True` לחילוץ זמני מילים ברמת מילישניות.
4. **רינדור שכבות גרפיות:**
   - יצירת כתוביות Heebo Black ותגיות הדגשה פיל ב-Chrome headless כשכבות PNG שקופות.
5. **עריכה סופית ב-ffmpeg (60 FPS):**
   - הרכבת פריימי הווידאו המונפשים + שכבות הכתוביות + דיבוב + מוזיקת רקע מונחתת + אפקטי סאונד ב-60 FPS.
6. **בקרת איכות (QC):**
   - משך כולל נמוך מ-60.00 שניות (אידיאלי: 50 עד 58 שניות).
   - אין פריימים קפואים או תמונות סטטיות ללא תנועת וידאו חיה.
   - תגית ההדגשה קופצת בדיוק על המילה המדוברת.
   - דיבוב ברור ומובן על גבי מוזיקת הרקע (מאסטרינג ב- -14 LUFS).

### מסלול ב': הקלטת מסך דמו סטודיו בדפדפן (Screen Studio 60 FPS Demo)
1. **הכנת סביבת האפליקציה:**
   - בדיקת זמינות השרת / ה-URL של האפליקציה (למשל `http://localhost:3000`).
   - הגדרת תבנית `templates/studio_recorder.html` עם כותרת הטאב, הכתובת וה-URL.
2. **בניית מנוע תנועה דטרמיניסטי (Deterministic Timeline):**
   - הגדרת שלבי הדמו ב-`window.studioSeek(t)`: תנועות עכבר חלקות (Ease-Out / Ease-InOut Cubic), לחיצות עם שקיעת עכבר טקטילית (scale 0.92) וגלי Ripple, הקלדה חיה אות-אחר-אות עם אירועי `input`, והצגת תגיות HUD צפות.
   - הגדרת מקצב נשימה של המצלמה: תקריב (1.26x-1.28x) בזמן הקלדה ממוקדת, וחזרה מהירה למבט רחב (1.0x) להצגת ההקשר המלא של שולחן העבודה והחלון הצף.
3. **רינדור 60 FPS ישיר מקומפוזיטור Chromium:**
   - הפעלת Chromium עם `--enable-begin-frame-control` ושימוש ב-`HeadlessExperimental.beginFrame` בהפרשי 16,666.67 µs.
   - הזרמת הפריימים כ-JPEG ישירות ל-FFmpeg דרך `stdin` (`image2pipe`).
4. **בקרת איכות (QC):**
   - וידוא קצב פריימים של 60.0 FPS ומשך מתוכנן באמצעות `ffprobe`.
   - וידוא 0 duplicate frames בזמן תנועה ואפס ghosting/טשטוש.
   - וידוא שהחלון הצף, הטפט והדוק נשמרים לאורך הסרטון במבטים הרחבים.
5. **שמירה כ-Artifact והצגה למשתמש:**
   - העתקת קובץ ה-MP4 לתיקיית ה-Artifacts והטמעה בעמוד סיכום עם נגן וידאו וגלריית פריימים.

ראו `reference/lessons.md` לפירוט לקחים טכניים, מקרי בוחן ומבנה קוד מלא.

