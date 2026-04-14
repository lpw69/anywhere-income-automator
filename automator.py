#!/usr/bin/env python3
"""
Anywhere Income - Newsletter Automator
"""

import os, re, sys, datetime, requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import anthropic

YOUTUBE_API_KEY      = os.environ["YOUTUBE_API_KEY"]
ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY      = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID       = os.environ["BEEHIIV_PUBLICATION_ID"]

DAYS_LOOKBACK        = 4
MIN_DURATION_MINS    = 8
MAX_TRANSCRIPT_CHARS = 14000

CHANNELS = [
    {"name": "Alex Hormozi",  "id": "UCct-f7gu5F2N58Yvgzq5m9Q"},
    {"name": "Liam Ottley",   "id": "UCDqbMFcSCIqV1EkJoIoagMg"},
    {"name": "Greg Isenberg", "id": "UCNjPtLWAHvinh_xlBnFAePA"},
    {"name": "Codie Sanchez", "id": "UC28n3FHeEBe53NfJGpqnxTQ"},
    {"name": "Noah Kagan",    "id": "UC53UHFmfKeBj1HWLn-Rp4Zw"},
    {"name": "Dan Koe",       "id": "UCnCikd0s4i9KoDtaHPlK-JA"},
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
        chunks = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
        return " ".join(c["text"] for c in chunks)
    except (TranscriptsDisabled, NoTranscriptFound):
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
        return None

    stats = get_video_stats([v["video_id"] for v in all_videos])
    candidates = []
    for v in all_videos:
        vid_id = v["video_id"]
        if vid_id not in stats: continue
        dur = parse_duration_mins(stats[vid_id]["contentDetails"]["duration"])
        if dur < MIN_DURATION_MINS: continue
        candidates.append({**v, "views": int(stats[vid_id]["statistics"].get("viewCount", 0)), "duration_mins": round(dur, 1)})

    for c in sorted(candidates, key=lambda x: x["views"], reverse=True):
        print(f"\nTrying: \"{c['title']}\" ({c['views']:,} views)")
        t = get_transcript(c["video_id"])
        if t:
            c["transcript"] = t
            return c
        print("  No transcript, trying next...")
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
    r = requests.post(
        f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/posts",
        headers={"Authorization": f"Bearer {BEEHIIV_API_KEY}", "Content-Type": "application/json"},
        json={"subject": subject, "preview_text": subject, "body": text_to_html(body_text),
              "status": "draft", "platform": "email",
              "meta_default_description": f"Auto-drafted from: {source_url}"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


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
    print(f"\n[OK] Draft posted. ID: {result.get('data', {}).get('id', 'unknown')}")
    print(f"     Review at: https://app.beehiiv.com/")


if __name__ == "__main__":
    main()
