#!/usr/bin/env python3
"""
Anywhere Income - Newsletter Automator

Scans YouTube channels, picks the most-viewed recent video,
fetches the transcript, generates a newsletter draft via Claude,
and emails it to Lewis via Gmail SMTP.

Required secrets:
  YOUTUBE_API_KEY
  ANTHROPIC_API_KEY
  SUPADATA_API_KEY
  GMAIL_USER          (your Gmail address)
  GMAIL_APP_PASSWORD  (16-char app password from myaccount.google.com/security)
"""

import os, re, sys, datetime, requests, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic

YOUTUBE_API_KEY     = os.environ["YOUTUBE_API_KEY"]
ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
SUPADATA_API_KEY    = os.environ["SUPADATA_API_KEY"]
GMAIL_USER          = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD  = os.environ["GMAIL_APP_PASSWORD"]
NOTIFY_EMAIL        = "lewis@underdog-ghostwriting.com"

DAYS_LOOKBACK       = 7
MIN_DURATION_MINS   = 8
MAX_TRANSCRIPT_CHARS = 14000

CHANNELS = [
    {"name": "Alex Hormozi",  "id": "UCUyDOdBWhC1MCxEjC46d-zw"},
    {"name": "Liam Ottley",   "id": "UCui4jxDaMb53Gdh-AZUTPAg"},
    {"name": "Greg Isenberg", "id": "UCPjNBjflYl0-HQtUvOx0Ibw"},
    {"name": "Codie Sanchez", "id": "UC5fI3kxC-ewZ6ZXEYgznM7g"},
    {"name": "Noah Kagan",    "id": "UCF2v8v8te3_u4xhIQ8tGy1g"},
    {"name": "Dan Koe",       "id": "UCWXYDYv5STLk-zoxMP2I1Lw"},
]

SYSTEM_PROMPT = """You write the Anywhere Income newsletter by Lewis, a British entrepreneur who left corporate IT to build location-independent income.

THREE-BUCKET FRAMEWORK (use only when natural):
- Tactical Income: matched betting, user testing, SERP clicks
- Active Service Income: freelance writing, design, video editing, voiceovers
- Cash-Flowing Assets: newsletter, outsourced businesses, long-term income machines

NEWSLETTER STRUCTURE:
1. Subject line
2. Opening hook (2-3 lines, sharp observation or surprising stat)
3. Core body (summarise the insight, Lewis's commentary, short paragraphs)
4. Natural transition then: --- [AD BREAK] ---
5. Post-ad continuation with practical takeaways
6. Sign-off from Lewis

STYLE (non-negotiable):
- First person, UK English, USD primary (GBP where relevant)
- Short mobile-friendly paragraphs
- Credit source creators properly
- No em dashes, no rhetorical question hooks
- No "Real Talk", "the bottom line", "here's the kicker", "not X not Y but Z"
- No fabricated stats or anecdotes
- No staccato sentences, no AI jargon

OUTPUT: Start with SUBJECT: [line] then the full email body."""


def get_recent_videos(channel_id, channel_name, days=DAYS_LOOKBACK):
    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
        "key": YOUTUBE_API_KEY, "channelId": channel_id, "part": "snippet",
        "type": "video", "publishedAfter": published_after, "maxResults": 10, "order": "date",
    }, timeout=15)
    r.raise_for_status()
    return [{"video_id": i["id"]["videoId"], "title": i["snippet"]["title"], "channel": channel_name}
            for i in r.json().get("items", [])]


def get_video_stats(video_ids):
    r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "key": YOUTUBE_API_KEY, "id": ",".join(video_ids), "part": "statistics,contentDetails",
    }, timeout=15)
    r.raise_for_status()
    return {i["id"]: i for i in r.json().get("items", [])}


def parse_duration_mins(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m: return 0
    h, mn, s = [int(x or 0) for x in m.groups()]
    return h * 60 + mn + s / 60


def get_transcript(video_id):
    try:
        r = requests.get(
            "https://api.supadata.ai/v1/youtube/transcript",
            headers={"x-api-key": SUPADATA_API_KEY},
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "text": "true"},
            timeout=30,
        )
        if r.status_code == 200:
            transcript = r.json().get("content", "")
            return transcript if transcript else None
        print(f"    Supadata error {r.status_code}: {r.text[:200]}")
        return None
    except Exception as e:
        print(f"    Transcript error: {e}")
        return None


def find_best_video():
    print("Scanning channels...")
    all_videos = []
    for ch in CHANNELS:
        try:
            vids = get_recent_videos(ch["id"], ch["name"])
            print(f"  {ch['name']}: {len(vids)} video(s)")
            all_videos.extend(vids)
        except Exception as e:
            print(f"  {ch['name']}: failed - {e}")

    if not all_videos:
        print("No recent videos found.")
        return None

    stats = get_video_stats([v["video_id"] for v in all_videos])
    candidates = []
    for v in all_videos:
        vid_id = v["video_id"]
        if vid_id not in stats: continue
        dur = parse_duration_mins(stats[vid_id]["contentDetails"]["duration"])
        if dur < MIN_DURATION_MINS: continue
        candidates.append({
            **v,
            "views": int(stats[vid_id]["statistics"].get("viewCount", 0)),
            "duration_mins": round(dur, 1),
        })

    if not candidates:
        print("No videos met the minimum duration requirement.")
        return None

    for c in sorted(candidates, key=lambda x: x["views"], reverse=True):
        print(f"\nTrying: \"{c['title']}\" ({c['views']:,} views, {c['duration_mins']} mins)")
        t = get_transcript(c["video_id"])
        if t:
            c["transcript"] = t
            print(f"  Transcript: {len(t):,} chars")
            return c
        print("  No transcript, trying next...")

    print("No candidates had a usable transcript.")
    return None


def generate_newsletter(video):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-opus-4-5", max_tokens=2000, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content":
            f"Source: \"{video['title']}\" by {video['channel']}\n"
            f"URL: https://youtube.com/watch?v={video['video_id']}\n\n"
            f"Transcript:\n{video['transcript'][:MAX_TRANSCRIPT_CHARS]}\n\n"
            f"Write the Anywhere Income newsletter draft."}],
    )
    return response.content[0].text


def parse_output(raw):
    lines = raw.strip().split("\n")
    subject, body_lines = "", []
    for line in lines:
        if line.startswith("SUBJECT:") and not subject:
            subject = line.replace("SUBJECT:", "").strip()
        else:
            body_lines.append(line)
    return subject, "\n".join(body_lines).strip()


BOLD_PATTERN = re.compile(r"\*(.+?)\*")

def body_to_html(text):
    """Convert plain text newsletter body to readable HTML email."""
    parts = ["<div style='font-family:Georgia,serif;font-size:16px;line-height:1.7;max-width:640px;margin:0 auto;color:#222;'>"]
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "--- [AD BREAK] ---" in line:
            parts.append("<hr style='border:none;border-top:1px solid #ddd;margin:32px 0;'>")
            parts.append("<p style='color:#999;font-size:13px;text-align:center;'>[AD PLACEMENT]</p>")
            parts.append("<hr style='border:none;border-top:1px solid #ddd;margin:32px 0;'>")
        else:
            formatted = BOLD_PATTERN.sub(r"<strong>\1</strong>", line)
            parts.append(f"<p style='margin:0 0 16px 0;'>{formatted}</p>")
    parts.append("</div>")
    return "\n".join(parts)


def send_draft_email(subject, body_text, source_url):
    """Email the full newsletter draft via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Draft Ready] {subject}"
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL

    plain_body = (
        f"New Anywhere Income newsletter draft is ready.\n\n"
        f"SUBJECT LINE: {subject}\n"
        f"SOURCE VIDEO: {source_url}\n\n"
        f"{'=' * 60}\n\n"
        f"{body_text}\n\n"
        f"{'=' * 60}\n"
        f"Copy the draft above into Beehiiv to review and publish.\n"
    )

    html_body = f"""
    <html><body>
    <div style="font-family:Arial,sans-serif;font-size:14px;color:#333;max-width:700px;margin:0 auto;">
      <div style="background:#f5f5f5;padding:16px 24px;border-radius:6px;margin-bottom:24px;">
        <p style="margin:0;font-size:13px;color:#666;">New Anywhere Income draft</p>
        <p style="margin:4px 0 0;font-size:18px;font-weight:bold;">{subject}</p>
        <p style="margin:8px 0 0;font-size:12px;color:#999;">Source: <a href="{source_url}">{source_url}</a></p>
      </div>
      <div style="border-left:3px solid #c8f542;padding-left:16px;margin-bottom:24px;">
        <p style="margin:0;font-size:12px;color:#999;text-transform:uppercase;letter-spacing:0.05em;">Newsletter draft</p>
      </div>
      {body_to_html(body_text)}
      <div style="background:#f5f5f5;padding:16px 24px;border-radius:6px;margin-top:32px;font-size:13px;color:#666;">
        Copy this draft into <a href="https://app.beehiiv.com">Beehiiv</a> to review and publish.
      </div>
    </div>
    </body></html>
    """

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_USER, [NOTIFY_EMAIL], msg.as_string())

    print(f"  Draft emailed to {NOTIFY_EMAIL}")


def main():
    print("=" * 55)
    print("  Anywhere Income Newsletter Automator")
    print(f"  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    video = find_best_video()
    if not video:
        sys.exit(1)

    print("\nGenerating draft via Claude...")
    raw = generate_newsletter(video)
    subject, body = parse_output(raw)
    if not subject:
        subject = f"Newsletter draft - {video['title'][:60]}"
    print(f"\nSubject: {subject}")

    source_url = f"https://youtube.com/watch?v={video['video_id']}"

    print("\nSending draft email...")
    send_draft_email(subject, body, source_url)

    print(f"\n[OK] Done. Draft emailed to {NOTIFY_EMAIL}")


if __name__ == "__main__":
    main()
