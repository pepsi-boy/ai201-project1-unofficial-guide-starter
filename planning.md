# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

My domain is Vanderbilt University dining hall experiences and student opinions about campus food options. This knowledge is valuable because students frequently rely on unofficial reviews and personal experiences when deciding where to eat, which meal plans are worthwhile, and which dining halls best fit their preferences. Much of this information is scattered across student newspapers, opinion magazines, and Reddit discussions, making it difficult to search and compare through official university resources alone.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | The Vanderbilt Hustler | Ranking of all 11 Vanderbilt dining options with pros & cons | https://vanderbilthustler.com/2023/04/23/a-ranking-of-vanderbilts-dining-options/ |
| 2 | The Vanderbilt Hustler | "Lots of change, some progress" — review of Campus Dining | https://vanderbilthustler.com/2022/09/27/lots-of-change-some-progress-a-review-of-campus-dining/ |
| 3 | The Vanderbilt Hustler | Student reviews of VandyCart / food beyond the dining hall | https://vanderbilthustler.com/2025/10/19/campus-food-beyond-the-dining-hall-student-reviews-of-vandycart/ |
| 4 | The Vanderbilt Hustler | "3 years of Campus Dining losses, ranked" (opinion) | https://vanderbilthustler.com/2024/09/01/3-years-of-campus-dining-losses-ranked/ |
| 5 | The Vanderbilt Hustler | Meal plan options updated after student feedback | https://vanderbilthustler.com/2024/10/20/dining-introduces-updated-meal-plan-options-following-student-feedback/ |
| 6 | The Vanderbilt Hustler | Recent changes to several dining locations (2026) | https://vanderbilthustler.com/2026/02/17/campus-dining-implements-changes-to-several-dining-locations/ |
| 7 | Vanderbilt Political Review | "Is the Vanderbilt Meal Plan Worth It?" — cost breakdown | https://vanderbiltpoliticalreview.com/6222/campus/is-the-vanderbilt-meal-plan-worth-it/ |
| 8 | Vanderbilt Business Review | All-you-care-to-eat vs. retail dining tradeoffs | https://vanderbiltbusinessreview.com/dining-halls-all-you-care-to-eat-vs-retail-dining/ |
| 9 | Reddit (r/Vanderbilt) | Student discussion thread on dining / meal plans (copy manually) | https://www.reddit.com/r/Vanderbilt/ (search "meal plan") |
| 10 | Reddit (r/Vanderbilt) | Student discussion thread on best/worst dining hall (copy manually) | https://www.reddit.com/r/Vanderbilt/ (search "dining hall") |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
