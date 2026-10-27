import asyncio
import os
import subprocess
import textwrap
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

OUT = Path("output")
OUT.mkdir(exist_ok=True)
AUDIO = OUT / "voice.mp3"
VIDEO = OUT / "aravicai-draft.mp4"
SCRIPT = OUT / "script.txt"

TITLE = "كيف يساعدك الذكاء الاصطناعي؟"
LINES = [
    "أهلًا بكم في أرافيك ذكاء.",
    "الذكاء الاصطناعي ليس مجرد روبوت يجيب عن الأسئلة.",
    "يمكنه مساعدتك في تلخيص المعلومات، وتعلّم المهارات، وتنظيم الأفكار.",
    "لكن تذكّر: تحقّق من المعلومات المهمة، ولا تشارك بياناتك الخاصة.",
    "تابع أرافيك ذكاء للمزيد من الشروحات التقنية باللغة العربية."
]
TEXT = " ".join(LINES)

def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    return None

def make_frames():
    font_path = find_font()
    try:
        title_font = ImageFont.truetype(font_path, 58) if font_path else ImageFont.load_default()
        body_font = ImageFont.truetype(font_path, 38) if font_path else ImageFont.load_default()
    except Exception:
        title_font = body_font = ImageFont.load_default()

    scenes = [
        ("أرافيك ذكاء", "المعرفة تبدأ بفكرة"),
        ("الذكاء الاصطناعي", "أداة تساعدك على التعلّم والإبداع"),
        ("استخدمه بوعي", "تحقّق من المعلومات واحمِ خصوصيتك"),
        ("تابعنا", "أرافيك ذكاء | محتوى تقني عربي")
    ]
    paths = []
    for i, (heading, subtitle) in enumerate(scenes):
        im = Image.new("RGB", (720, 1280), (9, 25, 52))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((36, 90, 684, 1190), radius=36, outline=(53, 145, 220), width=5)
        d.ellipse((245, 220, 475, 450), outline=(53, 145, 220), width=8)
        d.text((360, 330), "AI", font=title_font, fill=(255, 255, 255), anchor="mm")
        d.text((360, 600), heading, font=title_font, fill=(255, 255, 255), anchor="mm", direction="rtl")
        wrapped = textwrap.wrap(subtitle, width=25)
        y = 700
        for line in wrapped:
            d.text((360, y), line, font=body_font, fill=(190, 220, 245), anchor="mm", direction="rtl")
            y += 58
        d.text((360, 1080), "ARAVIC AI", font=body_font, fill=(95, 185, 255), anchor="mm")
        p = OUT / f"scene_{i:02d}.png"
        im.save(p)
        paths.append(p)
    return paths

async def make_audio():
    communicate = edge_tts.Communicate(TEXT, voice="ar-SA-HamedNeural", rate="-5%")
    await communicate.save(str(AUDIO))

def main():
    SCRIPT.write_text(TITLE + "\n\n" + TEXT + "\n", encoding="utf-8")
    asyncio.run(make_audio())
    frames = make_frames()
    # Each card is shown for 5 seconds; FFmpeg loops the generated scene sequence under narration.
    concat = OUT / "scenes.txt"
    with concat.open("w", encoding="utf-8") as f:
        for p in frames:
            f.write(f"file '{p.resolve()}'\n")
            f.write("duration 7\n")
        f.write(f"file '{frames[-1].resolve()}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(AUDIO), "-vf", "format=yuv420p", "-c:v", "libx264",
        "-preset", "ultrafast", "-tune", "stillimage", "-c:a", "aac",
        "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(VIDEO)
    ], check=True)
    print(f"Created {VIDEO}")

if __name__ == "__main__":
    main()
