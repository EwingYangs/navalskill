#!/usr/bin/env python3
"""
Build atomic knowledge library from scraped tweets.
Auto-detects topics from content, classifies type and confidence.
Usage: python3 build_atoms.py --handle naval --input tweets.json --output atoms.jsonl --topics topics.json
"""

import json
import re
import os
import argparse


def classify_type(text):
    """Classify tweet type."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["don't", "never", "avoid", "mistake", "wrong",
                                       "trap", "myth", "fallacy", "stop"]):
        if len(text) < 200:
            return "anti-pattern"
    if any(w in text_lower for w in ["how to", "step", "process", "method",
                                       "strategy", "technique", "way to", "approach"]):
        return "method"
    if any(w in text_lower for w in ["example", "story", "when i", "i once",
                                       "my experience", "case study"]):
        return "case"
    if any(w in text_lower for w in ["tool", "app", "software", "use this",
                                       "recommend", "try this"]):
        return "tool"
    if len(text) < 200 and not text.endswith("?"):
        return "principle"
    return "insight"


def classify_confidence(text, topics):
    if len(text) < 150 and len(topics) <= 2:
        return "high"
    if len(text) < 300 and len(topics) >= 1:
        return "medium"
    return "low"


def extract_knowledge(text):
    """Extract core knowledge point from tweet."""
    if len(text) <= 200:
        cleaned = re.sub(r'https?://\S+', '', text).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else text[:200]
    sentences = re.split(r'[.!?\n]', text)
    candidates = [s.strip() for s in sentences if len(s.strip()) > 20]
    if candidates:
        candidates.sort(key=len)
        return candidates[0][:200]
    return text[:200]


def classify_topics(text, topic_keywords):
    """Classify tweet into topics based on keyword matching."""
    text_lower = text.lower()
    scores = {}
    for topic, keywords in topic_keywords.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[topic] = score
    if not scores:
        return ["General"]
    sorted_topics = sorted(scores.items(), key=lambda x: -x[1])
    return [t[0] for t in sorted_topics[:3]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--handle', required=True)
    parser.add_argument('--input', required=True, help='Filtered tweets JSON')
    parser.add_argument('--output', required=True, help='Output atoms JSONL')
    parser.add_argument('--topics', required=True, help='Topics JSON: {"topic": ["keyword1", ...]}')
    parser.add_argument('--topic-skills', default=None, help='Topic-to-skills JSON: {"topic": ["skill1", ...]}')
    args = parser.parse_args()

    handle = args.handle.lstrip('@')

    with open(args.input) as f:
        tweets = json.load(f)

    with open(args.topics) as f:
        topic_keywords = json.load(f)

    topic_skills = {}
    if args.topic_skills and os.path.exists(args.topic_skills):
        with open(args.topic_skills) as f:
            topic_skills = json.load(f)

    print(f"Processing {len(tweets)} tweets with {len(topic_keywords)} topics...")

    atoms = []
    for i, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        if not text or len(text) < 15:
            continue

        topics = classify_topics(text, topic_keywords)
        tweet_type = classify_type(text)
        confidence = classify_confidence(text, topics)
        knowledge = extract_knowledge(text)

        # Map topics to skills
        skills = set()
        for t in topics:
            if t in topic_skills:
                skills.update(topic_skills[t])

        atom = {
            "id": f"{handle}_{i+1:04d}",
            "knowledge": knowledge,
            "original": text[:500],
            "url": tweet.get("url", ""),
            "date": tweet.get("time", "")[:10],
            "topics": topics,
            "skills": sorted(skills),
            "type": tweet_type,
            "confidence": confidence,
        }
        atoms.append(atom)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")

    print(f"Generated {len(atoms)} atoms → {args.output}")

    # Print stats
    from collections import Counter
    topic_counts = Counter()
    type_counts = Counter()
    for a in atoms:
        for t in a["topics"]:
            topic_counts[t] += 1
        type_counts[a["type"]] += 1

    print("\nTopics:")
    for t, c in topic_counts.most_common():
        print(f"  {t}: {c}")
    print("\nTypes:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
