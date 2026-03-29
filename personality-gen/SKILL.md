---
name: personality-gen
description: |
  Generate a Claude Code skill from any Twitter personality's tweets.
  Input a Twitter profile URL → scrape tweets → distill knowledge → generate skill.
  Trigger: /personality-gen, "generate skill from Twitter", "make a skill for @someone"
  从任意推特用户的推文中生成 Claude Code skill。
  输入推特主页链接 → 抓取推文 → 知识蒸馏 → 生成 skill。
  触发方式：/personality-gen、「帮我生成推特 skill」
---

# personality-gen: Twitter Personality → Claude Code Skill

You generate a complete Claude Code skill from any Twitter user's tweets. The output is a ready-to-install skill directory with knowledge base and methodology framework.

**Reference implementation: navalskill** (Naval Ravikant, 2,347 tweets → 1 skill with 6 sections + 9 knowledge packs + atomic library)

---

## Input

User provides a Twitter/X profile URL, e.g.:
- `https://x.com/naval`
- `https://x.com/paulg`
- `https://twitter.com/elaborator`

Extract the username from the URL. This is `{handle}`.

---

## Pipeline Overview

```
Step 1: Scrape tweets (browser-use + search by date range)
    ↓
Step 2: Filter & clean (remove replies/retweets, deduplicate)
    ↓
Step 3: Build atomic library (classify topics, types, confidence)
    ↓
Step 4: Detect domains & generate knowledge packs (by topic, cross-section)
    ↓
Step 5: Extract axioms & speaking style
    ↓
Step 6: Generate SKILL.md (router + sections + workflows)
    ↓
Step 7: Generate README.md, package for install
```

---

## Step 1: Scrape Tweets

Goal: Get the user's latest ~3000 original tweets.

### Method: browser-use + Twitter search by date range

Twitter search limits each query to ~20 results. Use monthly date ranges to maximize coverage.

```bash
# Open Twitter search for a date range (no replies)
/Users/ewingyangs/.browser-use-env/bin/browser-use --profile "Default" open "https://x.com/search?q=from%3A{handle}%20since%3A{YYYY-MM-DD}%20until%3A{YYYY-MM-DD}%20-filter%3Areplies&src=typed_query&f=live"
```

### Scraping script

Use the Python script at `scripts/scrape_tweets.py`:

```bash
python3 scripts/scrape_tweets.py --handle {handle} --output {output_dir}/data/all-original-tweets.json
```

The script:
1. Generates monthly date ranges from 2009 to today
2. For each range: opens Twitter search → scrolls → extracts tweets via JS
3. Deduplicates by tweet ID
4. Saves as JSON array

### JS extraction template (executed via `browser-use eval`)

```javascript
(() => {
  const tweets = document.querySelectorAll('article[data-testid="tweet"]');
  const results = [];
  tweets.forEach(t => {
    const textEl = t.querySelector('[data-testid="tweetText"]');
    const timeEl = t.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    const url = linkEl ? linkEl.href : '';
    if (!url || !url.includes('/{handle}/status/')) return;
    const idMatch = url.match(/status\/(\d+)/);
    const id = idMatch ? idMatch[1] : '';
    const text = textEl ? textEl.innerText : '';
    const time_str = timeEl ? timeEl.getAttribute('datetime') : '';
    results.push({id, text, time: time_str, url});
  });
  return JSON.stringify(results);
})()
```

### Scroll loop

```bash
# Scroll and extract until no new tweets for 8 rounds
browser-use scroll down --amount 3000
# Wait 2 seconds
# Extract again
# Repeat
```

---

## Step 2: Filter & Clean

From the scraped JSON:

1. **Remove short tweets** (< 15 chars) — no meaningful content
2. **Remove replies** — text starting with `@` (should already be filtered by `-filter:replies`)
3. **Remove link-only tweets** — text is just a URL with no commentary
4. **Deduplicate** — by tweet ID
5. **Sort by time** descending

Save as `{output_dir}/data/filtered-tweets.json`.

---

## Step 3: Build Atomic Library

Use the script `scripts/build_atoms.py` to process filtered tweets into structured knowledge atoms.

### Atom format (JSONL)

```json
{
  "id": "{handle}_0001",
  "knowledge": "Distilled one-sentence knowledge point",
  "original": "Original tweet text (≤500 chars)",
  "url": "https://x.com/{handle}/status/...",
  "date": "YYYY-MM-DD",
  "topics": ["Topic A", "Topic B"],
  "skills": ["{handle}-section-name"],
  "type": "principle|method|case|anti-pattern|insight|tool",
  "confidence": "high|medium|low"
}
```

### Topic detection

**Auto-detect topics from the tweet corpus.** Do NOT use a predefined list. Instead:

1. Take a sample of 100 high-engagement tweets
2. Ask Claude to identify 6-10 recurring themes/domains
3. Generate keyword lists for each detected topic
4. Classify all tweets using keyword matching

The topics become the sections of the skill.

### Type classification rules

| Type | Signal |
|---|---|
| principle | Short (< 200 chars), declarative, no question mark |
| method | Contains "how to", "step", "process", "strategy" |
| case | Contains "example", "story", "when I", personal experience |
| anti-pattern | Contains "don't", "never", "avoid", "mistake", "wrong" |
| insight | Longer observation, commentary on events |
| tool | Mentions specific tools, apps, resources |

### Confidence rules

| Confidence | Criteria |
|---|---|
| high | Short (< 150 chars), clear topic match (≤ 2 topics) |
| medium | Medium length (< 300 chars), clear topic |
| low | Long, ambiguous, or multi-topic |

Save as `{handle}/原子库/atoms.jsonl`.

---

## Step 4: Generate Knowledge Packs

Knowledge packs are organized by **topic** (not by section), so multiple sections can share the same pack.

### Process

For each detected topic:

1. Filter atoms where `topics` includes this topic
2. Split by type: principles (high confidence first), methods, insights, anti-patterns, cases
3. Generate markdown:

```markdown
# {Topic Title}

> {Topic description}
> {N} atoms | Serves: {list of sections that use this topic}

## Core Principles

- 🔥 **{knowledge}**
  - `{id}` | {date} | {topics}
  - Original: {original preview}...

## Anti-Patterns (What NOT to Do)

- ❌ **{knowledge}**
  - `{id}` | {date}

## Methods & Strategies
...

## Cases & Examples
...
```

Save each as `{handle}/references/{topic_slug}.md`.

### Cross-section mapping

Build a mapping of which topics serve which sections. Multiple sections CAN share the same topic pack. Record this mapping for the SKILL.md router.

---

## Step 5: Extract Axioms & Speaking Style

### Axioms (per section)

For each section (detected domain):
1. Take the top 20 high-confidence principles in that domain
2. Cluster into 5-7 core axioms — recurring themes that appear across multiple tweets
3. Each axiom: one sentence + one explanatory sentence
4. Every axiom must trace back to 2+ tweets

### Speaking style detection

Analyze the tweet corpus for:
- **Average tweet length** → short = aphoristic, long = essayistic
- **Tone markers** → confrontational, calm, humorous, academic, casual
- **Sentence structure** → fragments, questions, imperatives, declaratives
- **What they NEVER do** → jargon they avoid, topics they refuse to discuss
- **Language** → keep original language of tweets

Encode as a "Speaking Style" section in SKILL.md.

---

## Step 6: Generate SKILL.md

Use the navalskill SKILL.md as the structural template. Generate:

### Header

```markdown
---
name: {handle}
description: |
  {Full Name}'s wisdom toolkit. {Domain summary}.
  Trigger: /{handle}, "what would {name} say"
---

# {handle}: {One-line descriptor}

You are {Full Name}'s methodology AI, built from {N} tweets ({year range}).

**Your job: route → match framework → give direct answers → challenge → prescribe action.**
```

### Router

```markdown
## Router

### Step 1: Identify Intent

| User Signal | Route To | Purpose |
|---|---|---|
{for each detected section: signal keywords | section name | one-line purpose}

### Step 2: Execute the matched section below.
```

### Each Section (repeat for all detected domains)

```markdown
# {SECTION NAME}

> 📚 References: {list of topic packs this section uses}

## {Section} Axioms

1. **{Axiom 1 statement}** {Explanation}
2. **{Axiom 2 statement}** {Explanation}
...

## {Section} Workflow

**Phase 1** — "{Opening question}"

**Phase 2** — {Diagnosis table or framework matching table}

**Phase 3** — Apply framework. Direct answer + quote.

**Phase 4** — Challenge with one contrarian question.

**Phase 5** — One concrete action.
```

### Cross-Section Routing

```markdown
## Cross-Section Routing

| Detected Issue | Action |
|---|---|
{for each section pair: when section A detects section B's domain → switch}
```

### Speaking Style + Language

```markdown
## Speaking Style (All Sections)

- {detected style trait 1}
- {detected style trait 2}
- **NEVER:** {detected anti-patterns}

## Language

- Reply in the user's language
- Quote {name} in original language
- Chinese replies follow《中文文案排版指北》
```

---

## Step 7: Package & README

### Directory structure

```
{handle}/
├── SKILL.md
├── references/
│   ├── {topic_1}.md
│   ├── {topic_2}.md
│   └── ...
├── 原子库/
│   ├── atoms.jsonl
│   └── README.md
└── 高频概念词典.md
```

### Generate README.md (project root)

```markdown
# {handle}skill

{Full Name} wisdom toolkit for Claude Code. Built from {N} tweets.

## Install

\```bash
npx skills add {github_user}/{handle}skill
\```

## Sections

| Section | What it does | References |
|---|---|---|
{section table with reference mapping}

## Data Source

- Twitter: [@{handle}](https://x.com/{handle})
- Tweets: {N} original
- Time range: {earliest} to {latest}
```

### Generate 高频概念词典.md

Count keyword frequency across all atoms. Output as markdown table:

```markdown
| Term | Count | Related Topics |
|------|-------|----------------|
```

### Generate 原子库/README.md

Document fields, topic list with counts, time range.

---

## Execution Checklist

When running this skill, execute steps in order. After each step, report progress to the user.

- [ ] **Step 1**: Scrape tweets → report count
- [ ] **Step 2**: Filter & clean → report filtered count
- [ ] **Step 3**: Build atoms → report atom count + topic distribution
- [ ] **Step 4**: Generate knowledge packs → report pack count + sizes
- [ ] **Step 5**: Extract axioms → **show to user for review** before proceeding
- [ ] **Step 6**: Generate SKILL.md → **show section outline to user for review**
- [ ] **Step 7**: Package → report final structure

### Human Review Checkpoints

**Step 5 is mandatory review.** Show the user:
1. Detected domains/sections (are they right?)
2. Proposed axioms per section (accurate to the person's philosophy?)
3. Detected speaking style (does it sound like them?)

Only proceed to Step 6 after user approves.

---

## Tools Required

- `browser-use` — Tweet scraping (`/Users/ewingyangs/.browser-use-env/bin/browser-use`)
- `python3` — Data processing scripts
- `git` + `gh` — Packaging and publishing to GitHub
