#!/usr/bin/env python3
"""
Anywhere Income - Newsletter Automator

Scans YouTube channels, picks the most-viewed recent video,
fetches the transcript, generates a newsletter draft via Claude,
and saves it as a markdown file committed to the repo.

Required secrets:
  YOUTUBE_API_KEY
  ANTHROPIC_API_KEY
  SUPADATA_API_KEY
  GITHUB_TOKEN   (auto-provided by GitHub Actions)
"""

import os, re, sys, datetime, subprocess, requests
import anthropic

YOUTUBE_API_KEY      = os.environ["YOUTUBE_API_KEY"]
ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
SUPADATA_API_KEY     = os.environ["SUPADATA_API_KEY"]

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


def save_draft(subject, body_text, source_url):
    """Write draft to drafts/ folder and commit it to the repo."""
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    safe_subject = re.sub(r"[^a-z0-9]+", "-", subject.lower())[:60]
    filename = f"drafts/{date_str}-{safe_subject}.md"

    content = f"""# {subject}

**Date:** {date_str}
**Source:** {source_url}

---

{body_text}

---

*Copy into Beehiiv to review and publish.*
"""

    os.makedirs("drafts", exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)

    # Commit and push using the GITHUB_TOKEN already in the environment
    subprocess.run(["git", "config", "user.name", "Newsletter Bot"], check=True)
    subprocess.run(["git", "config", "user.email", "bot@noreply"], check=True)
    subprocess.run(["git", "add", filename], check=True)
    subprocess.run(["git", "commit", "-m", f"Draft: {subject[:72]}"], check=True)
    subprocess.run(["git", "push"], check=True)

    return filename


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

    print("\nSaving draft to repo...")
    source_url = f"https://youtube.com/watch?v={video['video_id']}"
    filename = save_draft(subject, body, source_url)

    print(f"\n[OK] Done.")
    print(f"     Draft saved: {filename}")
    print(f"     View at: https://github.com/lpw69/anywhere-income-automator/tree/main/drafts")


if __name__ == "__main__":
    main()
