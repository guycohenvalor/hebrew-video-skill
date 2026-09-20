# -*- coding: utf-8 -*-
"""
High-Impact Punch Conference Loop Renderer
- Visuals: Bold, provocative, minimalist poster-style animations with massive typography, neon glows, and impact zoom snaps
- Audio: Hall-shaking sub-bass landing sound effects on every scene transition + sidechain music ducking + peak limiter
- Output: out/Valor-ControlCenter-conference-punch.mp4 (and -vo.mp4 with --vo)
"""
import os, sys, json, subprocess, pathlib, urllib.request

HERE = pathlib.Path(".").resolve()
sys.path.insert(0, str(HERE))

import punch_animations

P = json.load(open("project.json", encoding="utf-8"))
WITH_VO = "--vo" in sys.argv
REBUILD = "--rebuild" in sys.argv

CHROME = P.get("chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
W, H, FPS = 1920, 1080, P.get("fps", 60)
BLACK, T = P.get("black_seconds", 1.0), P.get("xfade_seconds", 0.5)
TRANS = P.get("transitions", ["smoothright", "fade", "wiperight", "circleopen", "slideright", "fadegrays"])
RLM = "\u200f"
B = P["brand"]
MUSIC_ARG = None
OUT_ARG = None
for _idx, _arg in enumerate(sys.argv):
    if _arg == "--music" and _idx + 1 < len(sys.argv):
        MUSIC_ARG = sys.argv[_idx + 1]
    elif _arg == "--out" and _idx + 1 < len(sys.argv):
        OUT_ARG = sys.argv[_idx + 1]

DEFAULT_MUSIC = "assets/music/Presenterator.mp3"
MUSIC = MUSIC_ARG or DEFAULT_MUSIC
MGAIN = 0.85
SUB_SFX = "assets/sfx/sub_landing.wav"

if OUT_ARG:
    OUT = OUT_ARG
else:
    OUT = "out/Valor-ControlCenter-conference-punch-vo.mp4" if WITH_VO else "out/Valor-ControlCenter-conference-punch.mp4"

def rel(p): return "../" + p.replace("\\", "/")
LOGO = f'<img class="wordmark-img" src="{rel(B["logo"])}">' if os.path.exists(B.get("logo", "")) else ""
ROBOT = f'<img class="robot" src="{rel(B["robot"])}">' if os.path.exists(B.get("robot", "")) else ""

def qr_png():
    import qrcode
    p = HERE / "overlays" / "qr.png"
    if not p.exists():
        qrcode.make(C["contact"]["qr_url"], border=1, error_correction=qrcode.constants.ERROR_CORRECT_M).save(p)
    return "qr.png"

CARD_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:transparent; font-family:'Segoe UI', Arial, sans-serif; color:#fff; }}
.stage {{ position:absolute; inset:0; }}
.card {{ position:absolute; inset:0; display:flex; flex-direction:row; align-items:center; justify-content:center; gap:80px; padding:0 100px; }}
.cardtext {{ display:flex; flex-direction:column; align-items:center; gap:28px; max-width:1200px; text-align:center; }}
.robot {{ height:820px; width:auto; display:block; filter:drop-shadow(0 0 50px rgba(56,189,248,0.4)); -webkit-mask-image:radial-gradient(ellipse 60% 62% at 50% 50%,#000 58%,transparent 100%); }}
.wordmark-img {{ height:140px; width:auto; display:block; filter:drop-shadow(0 0 30px rgba(56,189,248,0.6)); }}
.h1 {{ font-size:92px; font-weight:900; letter-spacing:-1px; line-height:1.05; text-align:center; text-shadow:0 0 50px rgba(56,189,248,0.5); }}
.cta {{ font-size:62px; font-weight:800; color:#fff; line-height:1.35; }}
.cta .accent {{ color:#38bdf8; text-shadow:0 0 40px rgba(56,189,248,0.8); }}
.h2 {{ font-size:72px; font-weight:900; color:#fff; letter-spacing:2px; text-shadow:0 0 50px rgba(56,189,248,0.6); }}
.contact {{ font-size:44px; color:#cbd5e1; letter-spacing:.5px; line-height:1.5; font-weight:600; }}
.tag {{ font-size:36px; color:#38bdf8; letter-spacing:4px; font-weight:800; }}
.qr {{ width:400px; height:400px; background:#fff; padding:18px; border-radius:26px; display:block; box-shadow:0 0 60px rgba(56,189,248,0.5); border:3px solid #38bdf8; }}
.qrwrap {{ display:flex; flex-direction:column; align-items:center; gap:20px; }}
.qrlabel {{ font-size:34px; color:#94a3b8; letter-spacing:.5px; font-weight:700; }}
.hide {{ visibility:hidden; }}
"""

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

def png_of_card(name, body):
    html = HERE / "overlays" / f"punch_{name}.html"
    png = HERE / "overlays" / f"punch_{name}.png"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CARD_CSS}</style></head><body><div class="stage">{body}</div></body></html>', encoding="utf-8")
    if not png.exists():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={png}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    return str(png).replace("\\", "/")

def ff(args): subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]

def ease_out(var, delay, d, dist):
    return f"{dist}*pow(max(0,1-({var}-{delay})/{d}),3)"

def get_punch_card_bg():
    bg_png = HERE / "overlays" / "punch_card_bg.png"
    if not bg_png.exists():
        html = HERE / "overlays" / "punch_card_bg.html"
        html.write_text(f'''<!doctype html><html><head><meta charset="utf-8">
        <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ width:{W}px; height:{H}px; overflow:hidden; background:radial-gradient(circle at 50% 40%, #0d1322 0%, #05070b 80%); }}
        .punch-grid {{ position:absolute; inset:0; background-image:linear-gradient(rgba(56, 189, 248, 0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.06) 1px, transparent 1px); background-size:80px 80px; mask-image:radial-gradient(circle at 50% 45%, black 45%, transparent 85%); }}
        .punch-orb-cyan {{ position:absolute; width:900px; height:650px; border-radius:50%; background:radial-gradient(circle, rgba(56, 189, 248, 0.28) 0%, transparent 70%); top:50px; left:50%; transform:translateX(-50%); filter:blur(60px); }}
        </style></head><body>
        <div class="punch-grid"></div><div class="punch-orb-cyan"></div>
        </body></html>''', encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", f"--screenshot={bg_png}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    return str(bg_png).replace("\\", "/")

def build_punch_card(n, it, L):
    out = f"overlays/punch_seg{n}.mp4"
    if os.path.exists(out) and not REBUILD:
        return out
    kind = it["kind"]
    bg = get_punch_card_bg()
    a = png_of_card(f"{kind}_a", CARDS[kind]("a"))
    b = png_of_card(f"{kind}_b", CARDS[kind]("b"))
    
    # Impact Zoom Snap for punch cards too:
    slam_frames = 14
    kb = f"zoompan=z='if(lte(on,{slam_frames}), 1.08 - 0.08*on/{slam_frames}, 1.00 + 0.025*(on-{slam_frames})/({L*FPS}))':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS}"
    
    inputs = [
        "-f", "lavfi", "-i", f"color=c=0x05070b:s={W}x{H}:r={FPS}:d={L}",
        "-framerate", str(FPS), "-loop", "1", "-t", str(L), "-i", bg,
        "-framerate", str(FPS), "-loop", "1", "-t", str(L), "-i", a,
        "-framerate", str(FPS), "-loop", "1", "-t", str(L), "-i", b
    ]
    fc = [
        f"[0:v][1:v]overlay=0:0[bg_base]",
        f"[2:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[pa]",
        f"[bg_base][pa]overlay='{ease_out('t', 0, 0.7, -250)}':0[x]",
        f"[3:v]format=rgba,fade=t=in:st=0.25:d=0.4:alpha=1[pb]",
        f"[x][pb]overlay=0:'{ease_out('t', 0.25, 0.65, 50)}':enable='gte(t,0.25)'[y]",
        f"[y]scale={W*2}:{H*2}:flags=lanczos,{kb},format=yuv420p[v]"
    ]
    ff(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(L)] + ENC + [out])
    return out

def build_black(name, L):
    out = f"overlays/punch_{name}.mp4"
    if os.path.exists(out) and not REBUILD:
        return out
    ff(["-f", "lavfi", "-i", f"color=c=0x05070b:s={W}x{H}:r={FPS}:d={L}"] + ENC + [out])
    return out

def main():
    os.makedirs("overlays", exist_ok=True)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    
    items = P["timeline"]
    TOTAL = round(2 * BLACK + sum(float(i["dur"]) for i in items), 2)
    print(f"=== Building Punch Loop (Total duration: {TOTAL}s) ===")
    
    # 1. Build all clip segments
    clips = [(build_black("black0", BLACK + T), BLACK + T)]
    landing_timestamps = []
    current_time = BLACK
    
    for n, it in enumerate(items):
        L = round(float(it["dur"]) + T, 2)
        landing_timestamps.append(round(current_time, 2))
        current_time += float(it["dur"])
        
        seg_path = f"overlays/punch_seg{n}.mp4"
        if not os.path.exists(seg_path) or REBUILD:
            if it["kind"] == "shot":
                print(f"Building punch shot {n} (dur {L}s)...")
                punch_animations.build_punch_shot(n, it, L, HERE, CHROME, ff, ENC, W, H, FPS, RLM, ease_out)
            else:
                print(f"Building punch card {n} ({it['kind']}, dur {L}s)...")
                build_punch_card(n, it, L)
        else:
            print(f"Using cached punch seg {n}: {seg_path}")
        clips.append((seg_path, L))
        
    clips.append((build_black("black1", BLACK), BLACK))
    
    print("Landing timestamps (seconds):", landing_timestamps)
    
    # 2. Xfade video chain
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
    for path, _ in clips:
        cmd += ["-i", path]
        
    fc, prev, off, ti = [], "[0:v]", 0.0, 0
    for k in range(1, len(clips)):
        off = round(off + clips[k - 1][1] - T, 3)
        kinds = [None] + [i["kind"] for i in items] + [None]
        card_edge = "shot" not in (kinds[k - 1], kinds[k])
        tr = "fade" if card_edge else TRANS[ti % len(TRANS)]
        if not card_edge:
            ti += 1
        lab = f"[x{k}]" if k < len(clips) - 1 else "[vout]"
        fc.append(f"{prev}[{k}:v]xfade=transition={tr}:duration={T}:offset={off}{lab}")
        prev = lab
        
    fc[-1] = fc[-1].replace("[vout]", "[vx]")
    fc.append("[vx]format=yuv420p[vout]")
    maps = ["-map", "[vout]"]
    
    # 3. Audio Construction (Clean, cohesive, driving music without artificial transition booms)
    idx = len(clips)
    
    # Music Track
    cmd += ["-stream_loop", "-1", "-i", MUSIC]
    mus_idx = idx
    idx += 1
    fc.append(
        f"[{mus_idx}:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={TOTAL-2.0}:d=2.0,volume={MGAIN}[mus]"
    )
    alabs = ["[mus]"]
    
    if WITH_VO:
        vos = []
        for i, line in enumerate(P.get("narration_at", [])):
            vo_wav = f"assets/vo/loop{i}.wav"
            if os.path.exists(vo_wav):
                cmd += ["-i", vo_wav]
                fc.append(f"[{idx}:a]adelay={int(line['t']*1000)}|{int(line['t']*1000)}[vo{i}]")
                vos.append(f"[vo{i}]")
                idx += 1
        if vos:
            fc.append("".join(vos) + f"amix=inputs={len(vos)}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL}[voall]")
            fc.append("[voall]asplit=2[vo_sc][vo_aud]")
            fc.append("[mus][vo_sc]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=600:makeup=1[mus_ducked]")
            alabs = ["[mus_ducked]", "[vo_aud]"]
            
    # Output mix
    if len(alabs) > 1:
        fc.append(f"{''.join(alabs)}amix=inputs={len(alabs)}:normalize=0:dropout_transition=0,atrim=0:{TOTAL}[aout]")
    else:
        fc.append(f"{alabs[0]}atrim=0:{TOTAL}[aout]")
    maps += ["-map", "[aout]"]
    
    script = HERE / "overlays" / "punch_filter.txt"
    script.write_text(";".join(fc), encoding="utf-8")
    
    cmd += [
        "-/filter_complex", str(script),
    ] + maps + [
        "-t", str(TOTAL),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart",
        OUT
    ]
    
    print(f"Writing filter script: {script}")
    print(f"Executing final assembly to {OUT}...")
    subprocess.run(cmd, check=True)
    print(f"=== Successfully rendered punch loop: {OUT} ===")

if __name__ == "__main__":
    main()
