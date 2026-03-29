#!/usr/bin/env python3
"""
Scrape a Twitter user's tweets using browser-use + date-range search.
Usage: python3 scrape_tweets.py --handle naval --output ./data/all-original-tweets.json
"""

import json
import subprocess
import time
import os
import argparse
from datetime import datetime, timedelta

BROWSER_USE = "/Users/ewingyangs/.browser-use-env/bin/browser-use"
SCROLL_PAUSE = 2
MAX_STALE_ROUNDS = 8


def generate_monthly_ranges(start_year=2009, end_date=None):
    """Generate monthly date ranges from start_year to today."""
    if end_date is None:
        end_date = datetime.now()
    ranges = []
    current = datetime(start_year, 1, 1)
    while current < end_date:
        next_month = current + timedelta(days=32)
        next_month = next_month.replace(day=1)
        if next_month > end_date:
            next_month = end_date
        ranges.append((current.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d")))
        current = next_month
    return ranges


def run_bu(cmd):
    result = subprocess.run(
        [BROWSER_USE] + cmd,
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def make_js_extract(handle):
    return f'''
(() => {{
  const tweets = document.querySelectorAll('article[data-testid="tweet"]');
  const results = [];
  tweets.forEach(t => {{
    const textEl = t.querySelector('[data-testid="tweetText"]');
    const timeEl = t.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    const url = linkEl ? linkEl.href : '';
    if (!url || !url.includes('/{handle}/status/')) return;
    const idMatch = url.match(/status\\/(\\d+)/);
    const id = idMatch ? idMatch[1] : '';
    const text = textEl ? textEl.innerText : '';
    const time_str = timeEl ? timeEl.getAttribute('datetime') : '';
    results.push({{id, text, time: time_str, url, likes: 0, retweets: 0, views: 0}});
  }});
  return JSON.stringify(results);
}})()
'''


def extract_tweets(handle):
    output = run_bu(["eval", make_js_extract(handle)])
    for line in output.split('\n'):
        if line.startswith('result: '):
            return json.loads(line[len('result: '):])
    return []


def scroll_and_collect(all_tweets, handle):
    stale = 0
    round_num = 0
    while stale < MAX_STALE_ROUNDS:
        round_num += 1
        prev = len(all_tweets)
        try:
            tweets = extract_tweets(handle)
            for t in tweets:
                if t['id'] and t['id'] not in all_tweets:
                    all_tweets[t['id']] = t
        except Exception:
            stale += 1
            time.sleep(1)
            continue
        if len(all_tweets) == prev:
            stale += 1
        else:
            stale = 0
        run_bu(["scroll", "down", "--amount", "3000"])
        time.sleep(SCROLL_PAUSE)


def save(all_tweets, output_file):
    tweets_list = sorted(all_tweets.values(), key=lambda t: t.get('time', ''), reverse=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tweets_list, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Scrape tweets from a Twitter user')
    parser.add_argument('--handle', required=True, help='Twitter handle (without @)')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--target', type=int, default=3000, help='Target tweet count')
    args = parser.parse_args()

    handle = args.handle.lstrip('@')
    all_tweets = {}

    # Load existing if present
    if os.path.exists(args.output):
        with open(args.output) as f:
            for t in json.load(f):
                all_tweets[t['id']] = t
        print(f"Loaded {len(all_tweets)} existing tweets")

    # First: try profile page scroll
    print(f"Phase 1: Scrolling profile page for @{handle}...")
    try:
        run_bu(["close"])
    except Exception:
        pass
    time.sleep(1)
    run_bu(["--profile", "Default", "open", f"https://x.com/{handle}"])
    time.sleep(4)
    scroll_and_collect(all_tweets, handle)
    save(all_tweets, args.output)
    print(f"  Profile scroll: {len(all_tweets)} tweets")

    # Second: fill gaps with date-range search
    ranges = generate_monthly_ranges()
    print(f"Phase 2: Searching {len(ranges)} date ranges...")

    for i, (since, until) in enumerate(ranges):
        if len(all_tweets) >= args.target:
            print(f"\nReached target {args.target}!")
            break

        url = f"https://x.com/search?q=from%3A{handle}%20since%3A{since}%20until%3A{until}%20-filter%3Areplies&src=typed_query&f=live"
        prev = len(all_tweets)
        try:
            run_bu(["open", url])
            time.sleep(3)
            scroll_and_collect(all_tweets, handle)
        except Exception as e:
            print(f"  [{i+1}] Error: {e}")
            continue

        new = len(all_tweets) - prev
        if new > 0:
            print(f"  [{i+1}/{len(ranges)}] {since}→{until} +{new} → total {len(all_tweets)}")
            save(all_tweets, args.output)

    save(all_tweets, args.output)
    print(f"\nDone! Total: {len(all_tweets)} tweets → {args.output}")


if __name__ == '__main__':
    main()
