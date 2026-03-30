# navalskill

Naval Ravikant wisdom toolkit. Built from 2,347 tweets (2010-2026), distilled into knowledge atoms, and packaged as an AI agent skill.

**Inspired by [dbskill](https://github.com/dontbesilent2025/dbskill) — same architecture, different philosophy.**

---

## Install

```bash
npx skills add EwingYangs/navalskill
```

Or manually:

```bash
git clone https://github.com/EwingYangs/navalskill.git /tmp/navalskill && cp -r /tmp/navalskill ~/.claude/skills/navalskill && rm -rf /tmp/navalskill
```

After install, type `/naval` in Claude Code.

---

## What it does

One skill (`/naval`) with 6 sub-sections, auto-routed by intent:

| Section | What it does | References |
|---|---|---|
| **Wealth** | Specific knowledge, leverage, judgment, accountability | wealth_and_specific_knowledge, leverage_and_scale, technology_and_startups |
| **Happiness** | Desire, meditation, acceptance, inner peace | happiness_and_peace, philosophy_and_meaning, relationships_and_trust |
| **Decision** | Reversibility, long-term games, say no, clear thinking | decision_and_judgment, philosophy_and_meaning, relationships_and_trust |
| **Leverage** | Code, media, capital, labor — force multipliers | leverage_and_scale, wealth_and_specific_knowledge, technology_and_startups |
| **Reading** | Curiosity-driven learning, first principles, foundations | learning_and_reading, philosophy_and_meaning |
| **Health** | Body as foundation, daily habits, sleep, meditation | health_and_fitness, happiness_and_peace |

Sections cross-reference each other. For example:
- Wealth detects happiness issue → switches to Happiness
- Decision needs leverage analysis → switches to Leverage
- Health question is really anxiety → switches to Happiness

---

## Skill Structure

```
navalskill/
├── SKILL.md                        # Router + 6 sub-sections
├── references/                     # Knowledge packs (by topic, cross-section)
│   ├── wealth_and_specific_knowledge.md
│   ├── leverage_and_scale.md
│   ├── happiness_and_peace.md
│   ├── decision_and_judgment.md
│   ├── learning_and_reading.md
│   ├── health_and_fitness.md
│   ├── philosophy_and_meaning.md
│   ├── relationships_and_trust.md
│   └── technology_and_startups.md
├── atoms/                           # Structured knowledge database
│   ├── atoms.jsonl                  # 2,347 knowledge atoms
│   └── README.md                    # Field docs
└── frequency_dictionary.md          # High-frequency concept dictionary
```

Knowledge packs are organized by **topic** (not by skill section), so multiple sections can reference the same pack. No duplication.

---

## Knowledge Atoms

Each atom is a structured unit extracted from a tweet:

```json
{
  "id": "naval_0042",
  "knowledge": "You're not going to get rich renting out your time",
  "original": "You're not going to get rich renting out your time...",
  "url": "https://x.com/naval/status/...",
  "date": "2018-05-31",
  "topics": ["Wealth Creation", "Leverage & Scale"],
  "skills": ["naval-wealth", "naval-leverage"],
  "type": "principle",
  "confidence": "high"
}
```

### Standalone Usage

- **System prompt**: Paste any reference file into your AI's system prompt
- **RAG**: Import atoms.jsonl into your vector database (2,347 entries with topic tags)
- **Reference**: Read the knowledge packs as standalone methodology docs

---

## Difference from dbskill

| | dbskill (dontbesilent) | navalskill (Naval) |
|---|---|---|
| Source | 12,307 Chinese tweets | 2,347 English tweets |
| Domain | Business & entrepreneurship | Wealth, happiness & wisdom |
| Method | **Dissolve** questions (99% are wrong) | **Answer** questions (clear prescriptions) |
| Philosophy | Wittgenstein + Austrian economics | First principles + Stoicism + Buddhism |
| Style | Sharp, confrontational | Calm, aphoristic |
| Structure | Multiple skills (dbs, dbs-diagnosis, ...) | One skill, 6 internal sections |

---

## Data Source

- Twitter: [@naval](https://x.com/naval)
- Tweets: 2,347 original (no replies/retweets)
- Time range: 2010-12-08 to 2026-03-25
