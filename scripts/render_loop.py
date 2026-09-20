# -*- coding: utf-8 -*-
"""Animated conference loop (segments are cached in overlays/seg*.mp4; pass --rebuild after editing the timeline) from project.json → timeline (no narration, or `--vo` for the narration_at lines).
Run from the project folder.  Output: project.json → output (or output_vo with --vo).

Motion: every shot gets a Ken Burns move (zoom in/out + drift, cycling), text slides up + fades in, cards build in
layers (robot / QR slide in, text rises) with a slow push-in, and consecutive clips are joined with xfade transitions
(cycling through `transitions`). First and last `black_seconds` are pure black so the loop closes.
Audio: `music` (mp3/wav) trimmed to length, faded in/out, and ducked under the VO lines with sidechaincompress.
Timeline items: {"kind":"shot","src":<sec>,"dur":<sec>,"text":"..."} | {"kind":"close"|"contact","dur":<sec>}."""
import os, sys, json, subprocess, pathlib, urllib.request
HERE = pathlib.Path(".").resolve()
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))
try:
    import animations
except ImportError:
    animations = None
P = json.load(open("project.json", encoding="utf-8"))
WITH_VO = "--vo" in sys.argv
CHROME = P.get("chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
W, H, FPS = 1920, 1080, P.get("fps", 60)
FOOT = P["footage"]; FX, FY = P.get("footage_pos", [80, 80]); FW, FH = P.get("footage_size", [1760, 868])
BLACK, T = P.get("black_seconds", 1.0), P.get("xfade_seconds", 0.5)
TRANS = P.get("transitions", ["smoothright", "fade", "wiperight", "circleopen", "slideright", "fadegrays"])
KB = P.get("ken_burns", 0.07)
BT = P.get("big_text", {}); T_PX, T_BOTTOM = BT.get("font_px", 96), BT.get("bottom_px", 120)
B = P["brand"]; C = P["cards"]
OUT = P["output_vo"] if WITH_VO else P["output"]
MUSIC, MGAIN = P.get("music"), P.get("music_gain", 0.4)
RLM = "\u200f"
BGHEX = "0x" + B["bg"].lstrip("#")

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
body{{font-family:"Segoe UI","Segoe UI Variable",Arial,sans-serif;color:#fff}}
.stage{{position:absolute;inset:0}}
.big{{unicode-bidi:isolate;white-space:nowrap;position:absolute;left:50%;transform:translateX(-50%);max-width:1800px;bottom:{T_BOTTOM}px;text-align:center;font-size:{T_PX}px;font-weight:700;line-height:1.25;padding:22px 64px;border-radius:22px;background:rgba(15,17,21,.92);color:#fff;border:2px solid rgba(123,167,208,.55)}}
.big b{{font-weight:800}}
.card{{position:absolute;inset:0;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:70px;padding:0 100px}}
.cardtext{{display:flex;flex-direction:column;align-items:center;gap:30px;max-width:1200px;text-align:center}}
.robot{{height:820px;width:auto;display:block;-webkit-mask-image:radial-gradient(ellipse 60% 62% at 50% 50%,#000 58%,transparent 100%)}}
.wordmark-img{{height:150px;width:auto;display:block;filter:drop-shadow(0 0 24px rgba(123,167,208,.35))}}
.h1{{font-size:96px;font-weight:800;letter-spacing:-1px;line-height:1.05;text-align:center}}
.cta{{font-size:60px;font-weight:700;color:#fff;line-height:1.3}}
.cta .accent{{color:{B['accent']}}}
.h2{{font-size:64px;font-weight:700;color:#fff}}
.contact{{font-size:44px;color:#dfe6ef;letter-spacing:.5px;line-height:1.5}}
.tag{{font-size:34px;color:#9fb3c8;letter-spacing:1px}}
.qr{{width:420px;height:420px;background:#fff;padding:18px;border-radius:24px;display:block}}
.qrwrap{{display:flex;flex-direction:column;align-items:center;gap:16px}}
.qrlabel{{font-size:34px;color:#9fb3c8;letter-spacing:.5px}}
.frame{{position:absolute;left:{FX}px;top:{FY}px;width:{FW}px;height:{FH}px;border-radius:18px;box-shadow:0 30px 80px rgba(0,0,0,.6);border:1px solid rgba(255,255,255,.08)}}
.hide{{visibility:hidden}}
"""
def rel(p): return "../" + p.replace("\\", "/")
LOGO = f'<img class="wordmark-img" src="{rel(B["logo"])}">' if os.path.exists(B.get("logo", "")) else ""
ROBOT = f'<img class="robot" src="{rel(B["robot"])}">' if os.path.exists(B.get("robot", "")) else ""

def qr_png():
    import qrcode
    p = HERE / "overlays" / "qr.png"
    qrcode.make(C["contact"]["qr_url"], border=1, error_correction=qrcode.constants.ERROR_CORRECT_M).save(p); return "qr.png"

# Cards are rendered as two layers (a = picture side, b = text side) so each can animate on its own.
def card_close(layer):
    c = C["close"]; ha, hb = ("", "hide") if layer == "a" else ("hide", "")
    return (f'<div class="card"><div class="{ha}">{ROBOT}</div><div class="cardtext {hb}">{LOGO}<div class="h1">{c["h1"]}</div>'
            f'<div class="cta" dir="rtl">{RLM}{c["cta1"]}{RLM}<br>{RLM}<span class="accent">{c["cta2"]}</span>{RLM}</div></div></div>')
def card_contact(layer):
    c = C["contact"]; q = qr_png(); ha, hb = ("", "hide") if layer == "a" else ("hide", "")
    return (f'<div class="card"><div class="qrwrap {ha}"><img class="qr" src="{q}"><div class="qrlabel" dir="ltr">{c["qr_label"]}</div></div>'
            f'<div class="cardtext {hb}">{LOGO}<div class="h2" dir="rtl">{RLM}{c["h2"]}{RLM}</div>'
            f'<div class="contact" dir="rtl">{RLM}{c["line1"]}{RLM}<br><span dir="ltr">{c["line2"]}</span></div>'
            f'<div class="tag" dir="ltr">{c["tagline"]}</div></div></div>')
CARDS = {"close": card_close, "contact": card_contact}

def png_of(name, body):
    html = HERE / "overlays" / f"{name}.html"; png = HERE / "overlays" / f"{name}.png"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="stage">{body}</div></body></html>', encoding="utf-8")
    if not png.exists():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={png}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    return str(png).replace("\\", "/")

def ff(args): subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]

def ease_out(var, delay, d, dist):   # cubic ease-out from `dist` px offset to 0, starting at `delay`
    return f"{dist}*pow(max(0,1-({var}-{delay})/{d}),3)"

def kb_expr(n, L):
    """Ken Burns: cycle zoom-in centre / zoom-out centre / zoom-in drifting left / zoom-in drifting right."""
    frames = L * FPS; mode = n % 4
    if mode == 1: z = f"{1+KB}-{KB}*on/{frames}"
    else: z = f"1+{KB}*on/{frames}"
    if mode == 2: x = f"(iw-iw/zoom)*(0.5-0.5*on/{frames})"
    elif mode == 3: x = f"(iw-iw/zoom)*(0.5*on/{frames}+0.5)"
    else: x = "(iw-iw/zoom)/2"
    return f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d=1:s={FW}x{FH}:fps={FPS}"

def build_shot(n, it, L):
    if animations and (it.get("anim") or n in animations.SCENES):
        return animations.build_anim_shot(n, it, L, HERE, CHROME, CSS, ff, ENC, W, H, FPS, BGHEX, RLM, ease_out)
    out = f"overlays/seg{n}.mp4"; frame = png_of("frame", '<div class="frame"></div>')
    inputs = ["-f", "lavfi", "-i", f"color=c={BGHEX}:s={W}x{H}:r={FPS}:d={L}",
              "-ss", str(it["src"]), "-t", str(L), "-i", FOOT, "-loop", "1", "-t", str(L), "-i", frame]
    fc = [f"[1:v]scale={FW*2}:{FH*2}:flags=lanczos,{kb_expr(n, L)},format=rgba,fade=t=in:st=0:d=0.3:alpha=1[kb]",
          f"[0:v][kb]overlay={FX}:{FY}[a]", "[a][2:v]overlay=0:0[b]"]
    last = "[b]"
    if it.get("text"):
        p = png_of(f"text{n}", f'<div class="big" dir="rtl">{RLM}{it["text"]}{RLM}</div>')
        inputs += ["-loop", "1", "-t", str(L), "-i", p]
        fc += [f"[3:v]format=rgba,fade=t=in:st=0.25:d=0.4:alpha=1[tx]",
               f"[b][tx]overlay=0:'{ease_out('t', 0.25, 0.6, 70)}':enable='gte(t,0.25)'[c]"]; last = "[c]"
    fc.append(f"{last}format=yuv420p[v]")
    ff(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(L)] + ENC + [out]); return out

def build_card(n, it, L):
    out = f"overlays/seg{n}.mp4"; kind = it["kind"]
    a = png_of(f"{kind}_a", CARDS[kind]("a")); b = png_of(f"{kind}_b", CARDS[kind]("b"))
    inputs = ["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={L}",
              "-loop", "1", "-t", str(L), "-i", a, "-loop", "1", "-t", str(L), "-i", b]
    fc = [f"[1:v]format=rgba,fade=t=in:st=0:d=0.5:alpha=1[pa]",
          f"[0:v][pa]overlay='{ease_out('t', 0, 0.9, -320)}':0[x]",
          f"[2:v]format=rgba,fade=t=in:st=0.35:d=0.5:alpha=1[pb]",
          f"[x][pb]overlay=0:'{ease_out('t', 0.35, 0.8, 60)}':enable='gte(t,0.35)'[y]",
          f"[y]scale={W*2}:{H*2}:flags=lanczos,zoompan=z='1+0.035*on/{L*FPS}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS},format=yuv420p[v]"]
    ff(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(L)] + ENC + [out]); return out

def build_black(name, L):
    out = f"overlays/{name}.mp4"; ff(["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={L}"] + ENC + [out]); return out

def tts_line(i, text):
    V = P["voice"]; os.makedirs("assets/vo", exist_ok=True)
    mp3, wav = f"assets/vo/loop{i}.mp3", f"assets/vo/loop{i}.wav"
    if not os.path.exists(mp3):
        env_file = os.path.expanduser(V.get("env_file", "~/.config/valor-video/.env"))
        env = {l.split('=', 1)[0]: l.split('=', 1)[1].strip() for l in open(env_file, encoding="utf-8") if '=' in l and not l.startswith('#')}
        body = json.dumps({"text": text, "model_id": V.get("model_id", "eleven_v3"), "voice_settings": V.get("voice_settings", {})}).encode()
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V['voice_id']}?output_format=mp3_44100_192", body,
                                     {"xi-api-key": env["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
        open(mp3, "wb").write(urllib.request.urlopen(req, timeout=300).read())
    if not os.path.exists(wav): subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "2", wav])
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).decode().strip())
    return wav, d

# ---------------------------------------------------------------- build clips
os.makedirs("overlays", exist_ok=True); os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
REBUILD = "--rebuild" in sys.argv or not any(pathlib.Path("overlays").glob("seg*.mp4"))
for f in list(pathlib.Path("overlays").glob("*.png")) + (list(pathlib.Path("overlays").glob("*.mp4")) if REBUILD else []): f.unlink()
items = P["timeline"]; TOTAL = round(2 * BLACK + sum(float(i["dur"]) for i in items), 2)
clips = [(build_black("black0", BLACK + T) if REBUILD else "overlays/black0.mp4", BLACK + T)]
for n, it in enumerate(items):
    L = round(float(it["dur"]) + T, 2)
    if REBUILD: (build_shot if it["kind"] == "shot" else build_card)(n, it, L); print("clip", n, it["kind"], L, "s", flush=True)
    clips.append((f"overlays/seg{n}.mp4", L))
clips.append((build_black("black1", BLACK) if REBUILD else "overlays/black1.mp4", BLACK))

# ---------------------------------------------------------------- xfade chain
cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
for path, _ in clips: cmd += ["-i", path]
fc, prev, off, ti = [], "[0:v]", 0.0, 0
for k in range(1, len(clips)):
    off = round(off + clips[k - 1][1] - T, 3)
    kinds = [None] + [i["kind"] for i in items] + [None]           # kind per clip index
    card_edge = "shot" not in (kinds[k - 1], kinds[k])              # black↔anything, shot↔card, card↔card
    tr = "fade" if card_edge else TRANS[ti % len(TRANS)]
    if not card_edge: ti += 1
    lab = f"[x{k}]" if k < len(clips) - 1 else "[vout]"
    fc.append(f"{prev}[{k}:v]xfade=transition={tr}:duration={T}:offset={off}{lab}"); prev = lab
fc[-1] = fc[-1].replace("[vout]", "[vx]"); fc.append("[vx]format=yuv420p[vout]")
maps = ["-map", "[vout]"]; idx = len(clips); alabs = []

if MUSIC and os.path.exists(MUSIC):
    cmd += ["-stream_loop", "-1", "-i", MUSIC]
    fc.append(f"[{idx}:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
              f"afade=t=in:st=0:d=1.5,afade=t=out:st={TOTAL-2.5}:d=2.5,volume={MGAIN}[mus]"); idx += 1
    alabs.append("[mus]")
if WITH_VO:
    vos = []
    for i, line in enumerate(P.get("narration_at", [])):
        wav, d = tts_line(i, line["text"]); print(f"vo{i}: {d:.1f}s at {line['t']}s -> ends {line['t'] + d:.1f}s")
        cmd += ["-i", wav]; fc.append(f"[{idx}:a]adelay={int(line['t']*1000)}|{int(line['t']*1000)}[vo{i}]"); vos.append(f"[vo{i}]"); idx += 1
    if vos:
        fc.append("".join(vos) + f"amix=inputs={len(vos)}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL}[voall]")
        if alabs:   # duck the music under the voice
            fc.append("[voall]asplit[vk][vm]"); fc.append("[mus][vk]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=700:makeup=1[musd]")
            alabs = ["[musd]", "[vm]"]
        else: alabs = ["[voall]"]
if alabs:
    fc.append("".join(alabs) + (f"amix=inputs={len(alabs)}:normalize=0:dropout_transition=0," if len(alabs) > 1 else "") + f"atrim=0:{TOTAL}[aout]")
    maps += ["-map", "[aout]"]
script = HERE / "overlays" / "filter.txt"; script.write_text(";".join(fc), encoding="utf-8")
cmd += ["-/filter_complex", str(script)] + maps + ["-t", str(TOTAL), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p"]
if alabs: cmd += ["-c:a", "aac", "-b:a", "192k"]
cmd += ["-movflags", "+faststart", OUT]
print("clips:", len(clips), "total:", TOTAL, "s", flush=True)
subprocess.run(cmd, check=True)
print("done ->", OUT)
