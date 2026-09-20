# Lessons behind the pipeline (Control Center client video & Social Reels Studio)

## Why not HyperFrames
Three wipes in one day, each right after a `hyperframes render` failed/was stopped or `skills update` ran: the project folder, then all of `outputs/valor` (brief, rough cuts, keys, VO, user uploads), then the project again plus a backup folder two levels up. Nothing in the Recycle Bin. Also: its bundled chrome-headless-shell is blocked on this PC ("spawn UNKNOWN"; direct exec = Permission denied) and it needs `HYPERFRAMES_BROWSER_PATH` pointed at system Chrome. Banned.

## ElevenLabs facts
- `eleven_v3` is the only model listing Hebrew; it accepts `/with-timestamps`, so character timing for captions works.
- `eleven_multilingual_v2` speaks Hebrew unofficially but Guy rejected it as robotic.
- **PVC does not support Hebrew** (39 languages, none Hebrew) and trains only on Flash/Turbo/Multilingual v2; `eleven_v3` has `can_be_finetuned: false`. `POST /voices/pvc/{id}/train` answers `{"status":"ok"}` yet `fine_tuning.state` stays `{}` forever. Voice `ma6RJ8S3AeaumgehntdT` ("Guy Cohen HE PVC") was deleted and recreated on 4.9.2026 as `WZgqJaSYXQ2OtBWkc1zJ`; Guy wants it kept. The UI shows "not fine-tuned … instabilities" (expected for Hebrew). Do not delete account voices without asking.
- Instant clones from Guy's 32-min studio take: `jUf6zBvAkDrBllNnevJJ` (3-min slice), **`ND8JTbPy2RGiXF2rpt6p` (4×2.5-min slices) was chosen**. Older one-sample clones `pEC1hVCB2mYHhaaS3B9A` / `cJ6GWxLpNcAblrtC1aVv` are worse (D-style stability 1.0 distorts; the "Guy Voice" clone stresses רובוט on the wrong syllable).
- `eleven_multilingual_v2 + style 0.2 + speed 0.95` was the robotic combination; plain `stability 0.5 / similarity 0.75` on v3 won the A/B.
- Output `mp3_44100_192`, then transcode to 48 kHz stereo WAV for ffmpeg mixing (`amix normalize=0`).

## ffmpeg / Chrome details
- This ffmpeg build rejects `-filter_complex_script`; use `-/filter_complex <file>`.
- `boxblur=luma_r:luma_p:chroma_r:chroma_p` (chroma radius ≥ 7 fails on yuv420p).
- Overlays: `chrome.exe --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1920,1080 --default-background-color=00000000 --screenshot=<png> file:///…html` gives a true RGBA PNG; Segoe UI renders Hebrew correctly (in HyperFrames the same name was aliased to Roboto).
- Each overlay is its own ffmpeg input with `-loop 1 -t <dur>`, `setpts=PTS-STARTPTS+<start>/TB`, `fade=t=in:alpha=1`, and `overlay=…:enable='between(t,a,b)'`. 60+ inputs render fine.
- The user's own long PVC take: two m4a parts joined with `concat`, `pan=mono`, `highpass=f=70`, `volume=6dB` → peak −1.9 dB.

## Numbers that recur in Valor copy
21,876 runs / 90 days · 103 tracked processes · 34 with a clear rhythm · 3 machines · 59 % busiest · checks every 5 minutes · 17d 19h stuck job vs 1m 38s typical.

## Punch / High-Impact Editions (Lessons learned 6.9.2026, Manager sign-off)
- **Visuals**: Posters, big bold numbers (140-210px), dark cyber grid, 3-5 words per shot, zero micro-dashboard clutter. Legible from 10m away.
- **Audio DOs**: Use conventional, driving, upbeat corporate tech music (128-138 BPM, e.g. `Presenterator`, `Shiny Tech`). Master at ~ -13.4 LUFS. Continuous flow across all 60s.
- **Audio DONTs (Firm rule from management)**:
  1. Never add artificial explosion/sub-bass boom SFX (`sub_landing.wav`) between transitions every 4 seconds. Management finds them jarring, exaggerated, and cheap ("בומים מוגזמים ולא יפים").
  2. Never use aggressive sidechain ducking pump on cuts.
  3. Never choose dark industrial, dissonant, horror, or noisy tracks (like `REACTOR` with screeching at 00:40). Management finds them scary and intolerable ("רעש נוראי ומפחיד, מזוויע ב-00:40").
  4. Never use quiet elevator/piano music (`bed1` at 0.35 gain) when a punchy/kicking cut is requested.

## Hebrew stress (4.9.2026)
`eleven_v3` places stress on the last syllable of any Hebrew-script word and ignores nikud, hyphens, meteg and spacing for stress purposes (six spellings of בלוגים tested, all ba-lo-GIM). Loanwords that Israelis stress penultimately must be written in Latin script inside the Hebrew line ("בקבצי ה-log"), which is also what the caption shows. Nikud never reaches the screen: map it away in `display`. Scribe QA cannot catch stress errors because it strips nikud and returns consonants only, so send the user an mp3 instead.

---

## Vertical Shorts / Reels & Advanced Hebrew Synchronization (6.9.2026)

### 1. Pronunciation Stability and The "ערכה" Rule
- **Ambiguous Hebrew words break TTS:** Words without explicit vowels can fail silently or with wrong vowels and incorrect stress. For example, "ערכה" is frequently misread as "ARAKA" or stressed on the first syllable like English ("ÉR-ka") instead of Israeli Hebrew milra ("er-KÁ").
- **Do not fight the model with endless phonetic hacks:** Attempting to force stress with hyphens or question marks ("הער-כָּה ?") can introduce unnatural acoustic pauses or plosive bursts.
- **The Golden Replacement Rule:** If a Hebrew word fails in TTS or creates pronunciation ambiguity, **replace it immediately with an unambiguous synonym**. Changing "רוצים את הערכה המלאה ?" ל-"רוצים את החבילה המלאה ?" פתר את הבעיה בטייק ראשון בצליל טבעי וללא עמימות.
- **Loanwords and dagesh:** Loanwords like "טלפרומפטר" must be checked to ensure the Pe is pronounced hard (P, not F). If needed, write "טלפרומפטר" with dagesh or phonetically.
- **Never simulate organic human groans/snores:** Never attempt to generate snore sounds, grunts or sighing noises ("אה אה אה") via TTS. It sounds distorted, uncanny and grotesque. Keep the voice clean, articulate and professional, and let royalty-free fairy-tale background music and crisp UI sound effects (ping, sparkle, whoosh) tell the story.

### 2. Subtitle Synchronization and Dynamic Badge Design
- **Verbatim accuracy is non-negotiable:** Viewers read and listen simultaneously. Dropping even a single connective word (like "ללכת", "מהחיים", "בינה מלאכותית", "ממני") creates an immediate feeling of desynchronization.
- **Always extract centisecond word timestamps with Whisper:** Never estimate subtitle start and end times by ear. Run `faster-whisper` with `word_timestamps=True` directly on the final mixed/spliced audio.
- **Dynamic badge timing:** The visual highlight badge (yellow `#facc15` or cyan `#38bdf8`) must trigger at the exact millisecond the spoken word begins.
- **Word chunk density:** Limit subtitle chunks to 2 to 4 words per view. Long sentences clutter the screen and look like outdated corporate slides.
- **Typography:** Use **Heebo Black** (`font-weight: 900`, -0.5px letter-spacing). Never use default serif fonts or Segoe UI for social media reels.
- **Safe zones (9:16):**
  - General vertical dialogue: `bottom: 810px` (chest height) avoids both Instagram/TikTok bottom UI and top headers.
  - Scene-specific exceptions: If foreground subjects (e.g. dogs, laptops, desks) occupy the lower center, elevate the caption box to `bottom: 1020px` to prevent occlusion.

### 3. Vertical Video Engineering and Timing Budget
- **Duration limit:** Instagram Reels and YouTube Shorts strictly require < 60.00s. Target 50.0s to 58.5s (e.g. 52s או 58s). Anything at or beyond 60.00s breaks shorts categorization on platforms.
- **Audio mixing standards:** Master voiceover leveled to -14 LUFS, background music ducked to 0.08 with lowpass filter at 4500Hz to preserve voice intelligibility, and SFX aligned to millisecond cue marks.

---

## Post-to-Reel Transformation: Lessons from The Studio Video (סרטון הסטודיו מפוסט לינקדאין)

### 1. מלכודת התמונה הסטטית: מדוע זום ופאן אינם מספקים
בגרסה הראשונית של סרטון הסטודיו נלקחה תמונת הפוסט הראשית, נגזרו ממנה קרופים, והוחלו תנועות מצלמה עדינות של זום ופאן (Ken-Burns) ב-OpenCV/PIL.
התגובה הברורה מהמשתמש הייתה: **"צריך ממש אנימציה של התמונה ולא רק תמונה סטטית זהה עם כמה תנועות קטנות כמו שעשינו"**.
תמונה סטטית עם תנועות עדינות מרגישה לצופה ברשתות כמו שקופית פאוורפוינט ולא כמו סרטון רילס מקצועי. ברגע שיש אלמנטים בתמונה (דמות ישנה, רובוט מקליד, מסכים מרצדים), הקהל מצפה לתנועה חיה ואורגנית.

### 2. הפקת אנימציה גנרטיבית אמיתית (Image-to-Video Pipeline)
כדי לייצר אנימציה אמיתית מהאיור של הפוסט:
1. **גזירת קרופים אנכיים (9:16) ברזולוציה מקסימלית:** חותכים את התמונה הראשית לאזורי מיקוד (Focus Regions) לפי נושאי הסצנות (היוצר הישן, עמדת העבודה והרובוט, המסכים והטיים-ליין, ממשקי הטלפון).
2. **הזנה למודלי וידאו מבוססי תמונה (I2V):** שימוש במודלים מתקדמים כמו Kling AI, MiniMax (Hailuo), Runway Gen-3, Luma Dream Machine, או Wan 2.1.
3. **פרומפטי תנועה ייעודיים:**
   - *דמות אנושית*: נשימה טבעית (heaving chest with subtle breathing cycle), מצמוץ עיניים טבעי, חיוך עדין, תנועת ראש קלה ושינויי תאורת סביבה.
   - *רובוט ומחשבים*: זרוע רובוטית מכנית שמקלידה על מקלדת פיזית, מסכי עריכה שמרצדים ומציגים קוד רץ וגלי סאונד מונפשים, חלקיקי אבק באלומת אור.
   - *המחשת תסכול/כאב*: דיבור נמרץ למצלמה, תנועת יד מתוסכלת, ריצוד נורת חיווי אדומה כשהמיקרופון כבוי.

### 3. נוסחת לופ פינג-פונג (Ping-Pong Loop) להארכת תנועה רציפה
מודלי וידאו גנרטיביים מייצרים בדרך כלל 4 עד 5 שניות של וידאו, בעוד שביט בתסריט נמשך 7 עד 12 שניות. הקפאת הפריים בסוף הופכת את הווידאו לסטטי, וחיתוך חד לקובץ חדש יוצר קפיצה לא נעימה.
הפתרון הוא לופ פינג-פונג (קדימה ואחורה) מובנה ב-Python:
```python
def get_pingpong_frame(frame_index, total_source_frames):
    cycle = frame_index % (2 * (total_source_frames - 1))
    return cycle if cycle < total_source_frames else 2 * (total_source_frames - 1) - cycle
```
לופ זה מבטיח תנועה רציפה, חלקה וללא קפיצות לכל אורך הסצנה.

### 4. אלגוריתם נצנוץ כוכב יהלום (Diamond Sparkle Glint)
ברגעים של הישג, פריצת דרך, או קריאה לפעולה (CTA), אלמנט ויזואלי של כוכב מנצנץ מוסיף תחושת פרימיום.
במקום להדביק גיף שקוף, מופעל אלגוריתם שמשתמש בפוליגון יהלום וקרינה רדיאלית:
- פוליגון יהלום מרכזי (Diamond polygon) בלבן בוהק.
- זוהר רדיאלי רך (Soft radial glow) בגוון צהוב עדין (`255, 250, 220`).
- קרניים אלכסוניות קצרות וליבה מרכזית בוהקת.
- פונקציית מעבר סינוסית עולה ויורדת לפי התקדמות הזמן (progress 0.0 עד 1.0).

### 5. מבנה תסריט 6 הביטים מפוסט לריל (6-Beat Retention Blueprint)
- **סצנה 1 (0-8s):** הוק ותוצאה חלומית (יקיצה טבעית, 7 שעות שינה, אוטומציה שמצילה את המצב).
- **סצנה 2 (8-18s):** הכאב המשותף (שעתיים שהולכות לפח, 6 טייקים, מיקרופון כבוי).
- **סצנה 3 (18-29s):** נקודת השבירה (ישיבה מול תוכנת עריכה באמצע הלילה, החלטה לבנות פתרון).
- **סצנה 4 (29-38s):** מנוע הפתרון (איחוד יכולות לתוך חבילה אחת, ריל שלם בפקודה אחת).
- **סצנה 5 (38-50s):** הוכחה והדגמת מנגנון (טלפרומפטר, סלפי, כתוביות אוטומטיות, חיתוך שקט, דיבוב ElevenLabs).
- **סצנה 6 (50-58s):** קריאה לפעולה חברתית (כתבו "סטודיו" בתגובות ואשלח לכם הכל).

---

## Screen Studio & 60 FPS Browser Recording: Lessons from Cursor Benchmark (ספטמבר 2026)

### 1. מלכודת צילומי המסך המקוטעים מול הקלטת וידאו חיה
- כאשר משתמשים בצילומי מסך בודדים (Screenshots) ומחברים אותם לקובץ וידאו, התוצאה נראית כמו מצגת מקוטעת ולא כמו הדגמת כלי עובד.
- **הפתרון:** הקלטת Screencast רציפה ב-Playwright עם לכידת פריימים מלאה של תהליך העבודה, כולל הקלדה חיה, גלילה, מעבר בין טאבים ותנועת עכבר רציפה.

### 2. שמירה על עקביות קואורדינטות בזום (Coordinate Invariance)
- **הבעיה:** כאשר מבצעים זום מצלמה (`scale(1.35)`) על שולחן העבודה, אם העכבר הוירטואלי ממוקם מחוץ לאזור הזום (למשל על ה-viewport הראשי), הוא לא זז יחד עם הרכיבים ונוצרת סטייה של מאות פיקסלים (Drift).
- **הפתרון:** מיקום `#virtual-cursor` ו-`.click-ripple` כבנים ישירים של אלמנט `#desktop`.
  - העכבר מקבל קואורדינטות קבועות ביחס למסגרת שולחן העבודה (`x = 70 + el_x`, `y = 130 + el_y`).
  - כאשר `#desktop` משנה `scale` ו-`transform-origin`, העכבר והאפקטים גדלים וננעלים בצורה מושלמת על שדות הקלט והכפתורים ללא כל סטייה.

### 3. ארכיטקטורת 60 FPS אמיתית (True 60 FPS Compositor Stepping vs. Screencast Trap)
- **המלכודת של `record_video_dir` ב-Playwright/Chromium:**
  - מנגנון הקלטת הווידאו המובנה של Chromium (`record_video_dir`) נעול בקוד המקור C++ ל-25 FPS בלבד (`options.kDefaultFramesPerSecond = 25`).
  - הפיכת הקובץ ל-60 FPS באמצעות FFmpeg `-filter:v fps=60` אינה מוסיפה מידע — היא פשוט **משכפלת כל פריים פעמיים או שלוש** (A, A, B, B, B...). העין האנושית מבחינה מיד שהסרטון הוא למעשה ב-25 FPS.
  - ניסיון להשתמש באינטרפולציית תנועה של FFmpeg (`minterpolate` או `framerate=fps=60:interp_start=0:interp_end=255`) מייצר מריחת מעבר לינארית (Crossfade Blending) שיוצרת "עכבר רפאים" כפול (Ghost Double Cursor) וטשטוש אותיות שמשתמשים דוחים מיד ("זה עדיין 30FPS !!!", "לא עבד").
- **הפתרון המנצח: שליטה ישירה בקומפוזיטור (Compositor Stepping):**
  - הפעלת Chromium עם הדגלים:
    `--enable-begin-frame-control --run-all-compositor-stages-before-draw --disable-new-content-rendering-timeout --no-sandbox`.
  - פתיחת סשן CDP והפעלת `HeadlessExperimental.enable`.
  - קידום ציר הזמן באופן דטרמיניסטי במילישניות מדויקות (`window.studioSeek(t)`).
  - הפעלת `HeadlessExperimental.beginFrame` עם הפרש של 16,666.67 מיקרו-שניות לכל פריים (`interval=16666.67`).
  - הזרמת הפריימים (JPEG בייטים) ישירות לתוך ה-`stdin` של FFmpeg בצינור `image2pipe` (`-f image2pipe -vcodec mjpeg -r 60 -i - -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p output.mp4`).
- **תוצאות מדידה מוכחות (Verified Metrics):**
  - קצב פריימים: 60.0 FPS מדויק (3600 פריימים עבור 60 שניות).
  - דלתא בין פריימים בתנועה: **0 פריימים משוכפלים** (Duplicate Frames: 0 מתוך 119 במדידת מקטע תנועה).
  - **אפס טשטוש / Ghosting:** קווי מתאר של העכבר חדים ברמת הפיקסל הבודד.
  - מהירות הפקה: 20-25 FPS בזמן ריצה (סרטון של 60 שניות מתרנדר ומופק בפחות מ-3 דקות).

### 4. מקצב הנשימה של המצלמה (Dynamic Camera Breathing Cadence)
- **הלקח מסרטון המקור של Cursor:**
  - זום מתמיד (1.25x-1.35x) מוחק את שולי החלון, את הטפט ואת הדוק, והופך את הסרטון למסך רגיל ללא תחושת סטודיו.
  - בסרטון הבנצ'מרק של Cursor, המצלמה "נושמת":
    1. מתחילה במבט רחב מלא (1.0x) על הטפט ושולחן העבודה.
    2. מתקרבת (1.26x-1.28x) בזמן הקלדה ממוקדת בשדה כדי לאפשר קריאה קלה.
    3. **מיד עם סיום ההקלדה — חוזרת למבט רחב (1.0x)** כדי להציג את התעדכנות התוצאות בהקשר המלא של שולחן העבודה והחלון הצף.
    4. בבחינת טבלאות נתונים — זום עדין בלבד (1.08x) שמשאיר את שולי החלון וטפט שולחן העבודה בתמונה.
    5. סיום מלא ב-1.0x המציג את כל הנתונים, הדוק והטפט בסינרגיה מושלמת.


