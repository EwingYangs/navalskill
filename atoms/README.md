# 原子库说明

## 数据来源

- 推文总量：2,397 条（含过滤前）
- 筛选后实质性内容：2,347 条
- 最终知识原子：2,347 个
- 时间范围：2010-12-08 ~ 2026-03-25
- 来源：https://x.com/naval

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 格式：naval_{序号}，如 naval_0001 |
| knowledge | string | 提炼后的知识点（≤200 字） |
| original | string | 推文原文（≤500 字） |
| url | string | 推文链接 |
| date | string | 发布日期 |
| topics | string[] | 主题分类（10 类） |
| skills | string[] | 关联 Skill |
| type | string | principle / method / case / anti-pattern / insight / tool |
| confidence | string | high / medium / low |

## 主题分类（10 类）

| 主题 | 数量 | 说明 |
|------|------|------|
| Philosophy & Meaning | 911 | 哲学、存在意义、人性 |
| Technology & Startups | 697 | 技术、创业、AI |
| Wealth Creation | 492 | 财富创造、商业 |
| Relationships & Trust | 317 | 信任、关系、团队 |
| Learning & Reading | 288 | 阅读、学习、第一性原理 |
| Leverage & Scale | 218 | 杠杆、规模化 |
| Decision Making | 133 | 决策、判断力 |
| Mental Models | 130 | 心智模型、思维框架 |
| Happiness & Peace | 124 | 幸福、内心平静 |
| Health & Fitness | 124 | 健康、运动 |

## 文件结构

- `atoms.jsonl` — 全量（2,347 条）
