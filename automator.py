#!/usr/bin/env python3
"""
Anywhere Income - Newsletter Automator
"""

import os, re, sys, datetime, requests, smtplib
from email.mime.text import MIMEText
import anthropic

YOUTUBE_API_KEY      = os.environ["YOUTUBE_API_KEY"]
ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY      = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID       = os.environ["BEEHIIV_PUBLICATION_ID"]
SUPADATA_API_KEY     = os.environ["SUPADATA_API_KEY"]
NOTIFY_EMAIL         = "lewis@underdog-ghostwriting.com"

DAYS_LOOKBACK        = 7
MIN_DURATION_MINS    = 8
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

def text_to_html(text):
    parts = []
    for line in text.split("\n"):
        line = line.strip()
        if not line: continue
        if "--- [AD BREAK] ---" in line:
            parts.append("<!-- AD BREAK -->")
            parts.append("<p>&nbsp;</p>")
        else:
            formatted = BOLD_PATTERN.sub(r"<strong>\1</strong>", line)
            parts.append("<p>" + formatted + "</p>")
    return "\n".join(parts)


def post_to_beehiiv(subject, body_text, source_url):
    endpoint = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/posts"
    headers = {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "title": subject,
        "subject": subject,
        "preview_text": subject[:150],
        "content": {
            "free": {
                "web": text_to_html(body_text),
                "email": text_to_html(body_text),
            }
        },
        "status": "draft",
    }
    r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
    if not r.ok:
        print(f"  Beehiiv error {r.status_code}: {r.text[:500]}")
    r.raise_for_status()
    return r.json()


def send_notification(subject, source_url, post_id):
    """Send a plain email notification via GitHub Actions' built-in sendmail."""
    try:
        msg = MIMEText(
            f"A new Anywhere Income newsletter draft is ready to review.\n\n"
            f"Subject: {subject}\n"
            f"Source video: {source_url}\n"
            f"Beehiiv draft ID: {post_id}\n\n"
            f"Review and publish at: https://app.beehiiv.com/\n",
            "plain"
        )
        msg["Subject"] = f"[Anywhere Income] New draft ready: {subject[:60]}"
        msg["From"]    = "github-actions@noreply"
        msg["To"]      = NOTIFY_EMAIL

        with smtplib.SMTP("localhost") as smtp:
            smtp.sendmail(msg["From"], [NOTIFY_EMAIL], msg.as_string())
        print(f"  Notification sent to {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"  Notification skipped: {e}")


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

    print("\nPosting to Beehiiv...")
    source_url = f"https://youtube.com/watch?v={video['video_id']}"
    result = post_to_beehiiv(subject, body, source_url)
    post_id = result.get("data", {}).get("id", "unknown")

    print(f"\n[OK] Draft posted. ID: {post_id}")
    print(f"     Review at: https://app.beehiiv.com/")

    send_notification(subject, source_url, post_id)


if __name__ == "__main__":
    main()
