#!/usr/bin/env python3
"""
Generate topic-based knowledge packs and frequency dictionary from atoms.
Usage: python3 build_knowledge_packs.py --atoms atoms.jsonl --refs-dir ./references --dict-file 高频概念词典.md --topic-config topic_config.json
"""

import json
import os
import argparse
from collections import Counter, defaultdict


def build_pack(topic, config, atoms):
    """Build a knowledge pack for a topic."""
    matched = [a for a in atoms if topic in a.get("topics", [])]

    principles = [a for a in matched if a["type"] == "principle" and a["confidence"] == "high"]
    methods = [a for a in matched if a["type"] == "method"]
    anti_patterns = [a for a in matched if a["type"] == "anti-pattern"]
    cases = [a for a in matched if a["type"] == "case"]
    insights = [a for a in matched if a["type"] == "insight"]

    serves = config.get("serves", [])

    content = f"# {topic}\n\n"
    content += f"> {config.get('description', topic)}\n"
    content += f"> {len(matched)} atoms | Serves: {', '.join(serves)}\n\n\n"

    content += "## Core Principles\n\n"
    for a in principles[:40]:
        content += f"- 🔥 **{a['knowledge']}**\n"
        content += f"  - `{a['id']}` | {a['date']} | {', '.join(a['topics'])}\n"
        if a['original'] != a['knowledge'] and len(a['original']) > len(a['knowledge']) + 20:
            orig = a['original'][:200].replace('\n', ' ')
            content += f"  - Original: {orig}...\n"
        content += "\n"

    if anti_patterns:
        content += "\n## Anti-Patterns (What NOT to Do)\n\n"
        for a in anti_patterns[:20]:
            content += f"- ❌ **{a['knowledge']}**\n"
            content += f"  - `{a['id']}` | {a['date']}\n\n"

    if methods:
        content += "\n## Methods & Strategies\n\n"
        for a in methods[:15]:
            content += f"- **{a['knowledge']}**\n"
            content += f"  - `{a['id']}` | {a['date']}\n\n"

    if cases:
        content += "\n## Cases & Examples\n\n"
        for a in cases[:15]:
            orig = a['original'][:250].replace('\n', ' ')
            content += f"- **{a['knowledge']}**\n"
            content += f"  - `{a['id']}` | {a['date']}\n"
            content += f"  - {orig}\n\n"

    return content, len(matched)


def build_freq_dict(atoms, key_concepts):
    """Generate high-frequency concept dictionary."""
    concept_counts = Counter()
    concept_topics = defaultdict(Counter)

    for atom in atoms:
        text_lower = atom["original"].lower()
        for concept in key_concepts:
            if concept.lower() in text_lower:
                concept_counts[concept] += 1
                for topic in atom["topics"]:
                    concept_topics[concept][topic] += 1

    content = "# High-Frequency Concept Dictionary\n\n"
    content += f"> From {len(atoms)} knowledge atoms | {len([c for c, n in concept_counts.items() if n >= 3])} terms (≥3 occurrences)\n\n\n"
    content += "| Term | Count | Related Topics |\n"
    content += "|------|-------|----------------|\n"

    for concept, count in concept_counts.most_common():
        if count < 3:
            continue
        top_topics = concept_topics[concept].most_common(2)
        topics_str = ", ".join(t for t, _ in top_topics)
        content += f"| {concept} | {count} | {topics_str} |\n"

    return content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--atoms', required=True, help='Atoms JSONL file')
    parser.add_argument('--refs-dir', required=True, help='Output references directory')
    parser.add_argument('--dict-file', required=True, help='Output frequency dictionary file')
    parser.add_argument('--topic-config', required=True, help='Topic config JSON: {"topic": {"description": "...", "serves": [...]}}')
    parser.add_argument('--key-concepts', default=None, help='Key concepts JSON array for frequency dict')
    args = parser.parse_args()

    # Load atoms
    atoms = []
    with open(args.atoms) as f:
        for line in f:
            if line.strip():
                atoms.append(json.loads(line))
    print(f"Loaded {len(atoms)} atoms")

    # Load topic config
    with open(args.topic_config) as f:
        topic_config = json.load(f)

    os.makedirs(args.refs_dir, exist_ok=True)

    # Generate knowledge packs
    for topic, config in topic_config.items():
        content, count = build_pack(topic, config, atoms)
        slug = topic.lower().replace(' & ', '_and_').replace(' ', '_').replace('-', '_')
        path = os.path.join(args.refs_dir, f"{slug}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  {slug}.md: {count} atoms → serves {config.get('serves', [])}")

    # Generate frequency dictionary
    key_concepts = []
    if args.key_concepts and os.path.exists(args.key_concepts):
        with open(args.key_concepts) as f:
            key_concepts = json.load(f)
    else:
        # Auto-extract key concepts from all atom knowledge fields
        from collections import Counter
        word_counts = Counter()
        for a in atoms:
            words = a["knowledge"].lower().split()
            for w in words:
                if len(w) > 3:
                    word_counts[w] += 1
        key_concepts = [w for w, c in word_counts.most_common(100) if c >= 5]

    freq_dict = build_freq_dict(atoms, key_concepts)
    with open(args.dict_file, "w", encoding="utf-8") as f:
        f.write(freq_dict)
    print(f"  Frequency dictionary → {args.dict_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
