# -*- coding: utf-8 -*-
"""Render the video from project.json + vo.json: overlays via headless Chrome (RGBA PNG), one ffmpeg graph.
Run from the project folder after vo.py. Output: project.json → output."""
import os, json, subprocess, pathlib
HERE = pathlib.Path(".").resolve()
P = json.load(open("project.json", encoding="utf-8"))
VO = json.load(open("vo.json", encoding="utf-8"))
CHROME = P.get("chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
W, H = 1920, 1080
FPS = P.get("fps", 60)
FOOT = P["footage"]; FX, FY = P.get("footage_pos", [80, 80]); FW, FH = P.get("footage_size", [1760, 868])
PAD, CPAD = P.get("pad_seconds", 1.0), P.get("card_pad_seconds", 1.5)
CHIP_S = P.get("chip_seconds", 4)
CAP = P.get("caption", {}); CAP_PX, CAP_BOTTOM = CAP.get("font_px", 54), CAP.get("bottom_px", 110)
B = P["brand"]; C = P["cards"]
RLM = "\u200f"

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
body{{font-family:"Segoe UI","Segoe UI Variable",Arial,sans-serif;color:#fff}}
.stage{{position:absolute;inset:0}}
.chip{{unicode-bidi:isolate;position:absolute;top:96px;right:110px;padding:14px 28px;border-radius:999px;background:rgba(15,17,21,.88);border:2px solid {B['accent']};color:#fff;font-size:34px;font-weight:700}}
.cap{{unicode-bidi:isolate;white-space:nowrap;position:absolute;left:50%;transform:translateX(-50%);max-width:1760px;bottom:{CAP_BOTTOM}px;text-align:center;font-size:{CAP_PX}px;font-weight:600;line-height:1.3;padding:18px 40px;border-radius:16px;background:rgba(15,17,21,.9);color:#fff}}
.cap b{{font-weight:800}}
.card{{position:absolute;inset:0;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:70px;background:{B.get('card_bg','#000')};padding:0 100px}}
.cardtext{{display:flex;flex-direction:column;align-items:center;gap:26px;max-width:1150px;text-align:center}}
.robot{{height:820px;width:auto;display:block;-webkit-mask-image:radial-gradient(ellipse 60% 62% at 50% 50%,#000 58%,transparent 100%)}}
.wordmark-img{{height:150px;width:auto;display:block;filter:drop-shadow(0 0 24px rgba(123,167,208,.35))}}
.h1{{font-size:104px;font-weight:800;letter-spacing:-1px;line-height:1.05;text-align:center}}
.h2{{font-size:52px;font-weight:400;color:#c9d1dc}}
.accent{{color:{B['accent']}}}
.contact{{font-size:30px;color:#9fb3c8;letter-spacing:.5px}}
.cta{{font-size:44px;color:#fff;margin-top:10px}}
.stats{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:60px;background:{B['bg']}}}
.stat{{width:520px;height:360px;border-radius:24px;background:#171a21;border:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px}}
.stat .n{{font-size:120px;font-weight:800;color:{B['accent']};line-height:1}}
.stat .l{{font-size:36px;color:#dfe6ef;text-align:center;line-height:1.3}}
.frame{{position:absolute;left:{FX}px;top:{FY}px;width:{FW}px;height:{FH}px;border-radius:18px;box-shadow:0 30px 80px rgba(0,0,0,.6);border:1px solid rgba(255,255,255,.08)}}
"""
def rel(p): return "../" + p.replace("\\", "/")
LOGO = f'<img class="wordmark-img" src="{rel(B["logo"])}">' if os.path.exists(B.get("logo", "")) else ""
ROBOT = f'<img class="robot" src="{rel(B["robot"])}">' if os.path.exists(B.get("robot", "")) else ""
def card_title():
    t = C["title"]
    return f'<div class="card">{ROBOT}<div class="cardtext">{LOGO}<div class="h1">{t["h1"]}</div><div class="h2" dir="rtl">{RLM}{t["h2"]}{RLM}</div><div class="h2" dir="ltr" style="font-size:44px;letter-spacing:1px">{t.get("tagline","")}</div></div></div>'
def card_stats():
    return '<div class="stats">' + "".join(f'<div class="stat"><div class="n">{s["n"]}</div><div class="l" dir="rtl">{s["l"]}</div></div>' for s in C["stats"]) + '</div>'
def card_close():
    c = C["close"]
    return f'<div class="card">{ROBOT}<div class="cardtext">{LOGO}<div class="h2" dir="rtl" style="font-size:56px;color:#fff">{RLM}{c["h2"]}{RLM}</div><div class="cta" dir="rtl">{c["cta"]}</div><div class="contact" dir="rtl">{c["contact"]}</div></div></div>'
CARDS = {"title": card_title, "stats": card_stats, "close": card_close, "frame": lambda: '<div class="frame"></div>'}

def png_of(name, body):
    html = HERE / "overlays" / f"{name}.html"; png = HERE / "overlays" / f"{name}.png"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="stage">{body}</div></body></html>', encoding="utf-8")
    if not png.exists():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={png}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    return str(png).replace("\\", "/")

os.makedirs("overlays", exist_ok=True); os.makedirs(os.path.dirname(P["output"]) or ".", exist_ok=True)
for f in pathlib.Path("overlays").glob("*.png"): f.unlink()      # overlays are cheap; never serve stale ones
segs, t = [], 0.0
for n, (sc, vo) in enumerate(zip(P["scenes"], VO)):
    st = round(t, 2); du = round(vo["duration"] + (CPAD if sc["kind"] in ("title", "close") else PAD), 2)
    segs.append((n, sc, vo, st, du, round(st + du, 2))); t += du
TOTAL = round(t, 2)

cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-f", "lavfi", "-i", f"color=c=0x{B['bg'].lstrip('#')}:s={W}x{H}:r={FPS}:d={TOTAL}"]
vf, af, idx, chain = [], [], 1, "[0:v]"
def overlay(i, x, y, st, end, fade=0.0):
    global chain
    f = f"[{i}:v]format=rgba" + (f",fade=t=in:st=0:d={fade}:alpha=1" if fade else "") + f",setpts=PTS-STARTPTS+{st}/TB[o{i}]"
    vf.append(f); vf.append(f"{chain}[o{i}]overlay={x}:{y}:eof_action=pass:enable='between(t,{st},{end})'[v{i}]"); chain = f"[v{i}]"
frame_png = png_of("frame", CARDS["frame"]())
for (n, sc, vo, st, du, end) in segs:
    if sc["kind"] == "shot":
        cmd += ["-ss", str(sc["src"]), "-t", str(du), "-i", FOOT]; overlay(idx, FX, FY, st, end, 0.4); idx += 1
        cmd += ["-loop", "1", "-t", str(du), "-i", frame_png]; overlay(idx, 0, 0, st, end); idx += 1
        if sc.get("chip"):
            p = png_of(f"chip{n}", f'<div class="chip" dir="rtl">{RLM}{sc["chip"]}{RLM}</div>')
            cmd += ["-loop", "1", "-t", str(CHIP_S), "-i", p]; overlay(idx, 0, 0, st + 0.3, round(st + 0.3 + CHIP_S, 2), 0.4); idx += 1
    else:
        p = png_of(sc["kind"], CARDS[sc["kind"]]())
        cmd += ["-loop", "1", "-t", str(du), "-i", p]; overlay(idx, 0, 0, st, end, 0.6); idx += 1
    for j, c in enumerate(vo["captions"]):
        cs = round(st + c["start"], 2); cd = round(max(c["end"] - c["start"], 1.2), 2)
        p = png_of(f"cap{n}_{j}", f'<div class="cap" dir="rtl">{RLM}{c["text"]}{RLM}</div>')
        cmd += ["-loop", "1", "-t", str(cd), "-i", p]; overlay(idx, 0, 0, cs, round(cs + cd, 2), 0.25); idx += 1
    cmd += ["-i", vo["file"]]; af.append(f"[{idx}:a]adelay={int(st*1000)}|{int(st*1000)}[a{idx}]"); idx += 1

amix = "".join(f"[a{i}]" for i in range(1, idx) if f"[a{i}]" in "".join(af))
vf.append(f"{chain}format=yuv420p[vout]")
filt = ";".join(vf + af + [f"{amix}amix=inputs={len(af)}:normalize=0:dropout_transition=0[aout]"])
script = HERE / "overlays" / "filter.txt"; script.write_text(filt, encoding="utf-8")
cmd += ["-/filter_complex", str(script), "-map", "[vout]", "-map", "[aout]", "-t", str(TOTAL),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", P["output"]]
print("inputs:", idx, "total:", TOTAL, "s", flush=True)
subprocess.run(cmd, check=True)
print("done ->", P["output"])
