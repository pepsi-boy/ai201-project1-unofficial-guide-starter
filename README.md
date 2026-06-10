# The Unofficial Guide — Project 1

A RAG (Retrieval-Augmented Generation) system that makes student-generated
knowledge about **Vanderbilt University dining** searchable and answerable.
Ask a plain-language question and get a grounded, cited answer drawn from real
student reviews, the student newspaper, and Reddit threads.

**Pipeline:** Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
**Stack:** Python · sentence-transformers (`all-MiniLM-L6-v2`) · ChromaDB · Groq (`llama-3.3-70b-versatile`) · Gradio

```bash
# 1. set up env + install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your GROQ_API_KEY

# 2. build the pipeline
python ingest.py              # documents/ -> chunks.json (150 chunks)
python embed.py               # chunks.json -> ChromaDB vector store

# 3. launch the UI
python app.py                 # http://localhost:7860
```

---

## Domain

This system covers **Vanderbilt University dining hall experiences and student
opinions about campus food** — which dining halls are worth the walk, whether
the meal plan is worth its cost, and what the day-to-day food and service are
actually like. This knowledge is valuable because students rely on unofficial
reviews and personal experience when deciding where to eat, but it is scattered
across the student newspaper, opinion magazines, and Reddit threads. The
official Campus Dining website lists hours and menus but never says a dining
hall has long lines, overcooks its food, or that the meal plan carries a ~394%
per-meal premium — so this real, opinionated knowledge is hard to search or
compare through official channels.

---

## Document Sources

10 documents spanning four perspectives (dining-hall rankings, meal-plan value,
food-quality trends, and raw student discussion) so the corpus answers a range
of questions rather than repeating one viewpoint.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | The Vanderbilt Hustler — "A ranking of Vanderbilt's dining options" | Student newspaper (opinion/ranking) | https://vanderbilthustler.com/2023/04/23/a-ranking-of-vanderbilts-dining-options/ |
| 2 | The Vanderbilt Hustler — "Lots of change, some progress: A review of Campus Dining" | Student newspaper (review) | https://vanderbilthustler.com/2022/09/27/lots-of-change-some-progress-a-review-of-campus-dining/ |
| 3 | The Vanderbilt Hustler — "Student reviews of VandyCart" | Student newspaper (reviews) | https://vanderbilthustler.com/2025/10/19/campus-food-beyond-the-dining-hall-student-reviews-of-vandycart/ |
| 4 | The Vanderbilt Hustler — "3 years of Campus Dining losses, ranked" | Student newspaper (opinion) | https://vanderbilthustler.com/2024/09/01/3-years-of-campus-dining-losses-ranked/ |
| 5 | The Vanderbilt Hustler — "Dining introduces updated meal plan options" | Student newspaper (news) | https://vanderbilthustler.com/2024/10/20/dining-introduces-updated-meal-plan-options-following-student-feedback/ |
| 6 | The Vanderbilt Hustler — "Campus Dining implements changes to several dining locations" | Student newspaper (news) | https://vanderbilthustler.com/2026/02/17/campus-dining-implements-changes-to-several-dining-locations/ |
| 7 | Vanderbilt Political Review — "Is the Vanderbilt Meal Plan Worth It?" | Opinion magazine (analysis) | https://vanderbiltpoliticalreview.com/6222/campus/is-the-vanderbilt-meal-plan-worth-it/ |
| 8 | Vanderbilt Business Review — "Dining Halls: All You Care to Eat vs Retail Dining" | Student magazine (analysis) | https://vanderbiltbusinessreview.com/dining-halls-all-you-care-to-eat-vs-retail-dining/ |
| 9 | Reddit r/Vanderbilt — dining hall quality thread ("How are OUR dining halls") | Reddit discussion | reddit_dining_hall_thread.txt (from reddit.com/r/Vanderbilt) |
| 10 | Reddit r/Vanderbilt — meal plan / dining failures thread | Reddit discussion | reddit_mealplan_thread.txt (from reddit.com/r/Vanderbilt) |

Each source was copied into a plain `.txt` file in `documents/`, one file per
source, so retrieval can attribute every answer to a specific document.

---

## Chunking Strategy

**Chunk size:** ~600 characters (target), split on paragraph/sentence boundaries
rather than a hard character cut.

**Overlap:** ~100 characters between adjacent chunks.

**Why these choices fit your documents:** The corpus has two distinct shapes.
The long-form articles (e.g. the Hustler ranking) bury a useful fact about one
dining hall inside a 2,000-word piece, so I want each paragraph-sized idea in
its own chunk. The Reddit comments are the opposite — each is already a
complete, 1–2 sentence opinion. ~600 characters is roughly one substantial
paragraph or 2–4 short Reddit comments: large enough to carry a complete
thought, small enough that a specific query isn't diluted by unrelated content.
Splitting on paragraph/sentence boundaries (instead of a hard 600-char cut)
avoids slicing a sentence in half. The ~100-char overlap exists so a fact that
straddles a boundary (e.g. a verdict in one chunk, its reasoning in the next)
stays interpretable.

**Preprocessing before chunking** (`clean_text()` in `ingest.py`): strip the
UTF-8 BOM left by copy-paste, drop trailing author bios (everything after
"About the Contributors"), remove Reddit UI artifacts (`Upvote`, `Downvote`,
`Go to comments`, bare vote-count numbers, `Tags:`), and collapse blank lines.

**Final chunk count:** **150 chunks** across 10 documents (avg 486 chars,
range 147–697).

### Sample Chunks (5, each labeled with its source)

**1 — `hustler_dining_ranking.txt` (chunk #0)**
> A ranking of Vanderbilt's dining options After visiting Vanderbilt's dining locations, we ranked them based on setting, quality of food and atmosphere. "Hurry! We have to make it to the Rand line before everyone else gets there."

**2 — `political_review_mealplan.txt` (chunk #4)**
> behind the meal plan to see if students are really receiving a good value for what they paid. According to the US Bureau of Labor Statistics, the average American spends $2.42 per meal. So why is it that Vanderbilt freshmen are left paying $7.42/meal while upperclassmen on a 14-meal plan pay $9.55/meal? The majority of students are paying up to a 394% premium to eat on campus, with students living in Kissam paying a 400% premium due to higher priced meal plans.

**3 — `business_review_aycte_vs_retail.txt` (chunk #0)**
> Dining Halls: All You Care to Eat vs Retail Dining ... On the Campus Dining website, the two types are labeled as "Residential Dining Halls" and "Retail Dining". Residential Dining Halls include Commons, E. Bronson Ingram, Nicholas S. Zeppos, and Rothschild Dining Center. Retail Dining includes 2301 Allergen Free, Kitchen at Kissam, Rand Dining Center, and The Pub at Overcup Oak.

**4 — `reddit_dining_hall_thread.txt` (chunk #2)**
> ... roth: custom stir fry but lines can be long. beef korma and pho are solid. pub: burgers, wings, quesadillas, fries, etc. pretty fire. ... rand: mongolian (specifically the commodore tso chicken), randwich, rand cookie good ebi: can be sometimes good but can also be mid ... kissam: overall food quality is pretty bad, more misses than hits. they always manage to overcook their shit to oblivion.

**5 — `hustler_dining_changes_2026.txt` (chunk #0)**
> Campus Dining implements changes to several dining locations ... These changes include a new bagel bar in Commons, rotating desserts at EBI and flatbread pizzas at Rand. There is also now a daily limit of three meal swipes at Suzie's locations.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers. It runs locally
with no API key and no rate limits, produces 384-dim embeddings, and is more
than adequate for a 150-chunk corpus. Chunks are stored in **ChromaDB** with
**cosine distance** (`hnsw:space: cosine`) and source metadata. Retrieval uses
**top-k = 5**.

**Production tradeoff reflection:** If I were deploying this for real users and
cost weren't a constraint, I'd weigh:
- **Accuracy on domain-specific / informal text** — a larger model (e.g. OpenAI
  `text-embedding-3-large`) would better distinguish near-duplicate opinions and
  handle slangy Reddit phrasing, which (see Failure Case) MiniLM struggled with.
- **Context length** — MiniLM truncates around 256 tokens; fine for my 600-char
  chunks, but a larger input window would let me chunk less aggressively.
- **Multilingual support** — unnecessary for an English-only campus corpus, but
  it would matter for an international audience.
- **Local vs. API / latency** — local MiniLM means zero per-query cost and full
  data privacy; an API model adds latency and recurring cost but is typically
  more accurate. For a free student project, local wins; at scale, I'd revisit.

---

## Grounded Generation

**System prompt grounding instruction** (`query.py`): the model is told to
answer using **only** the provided context and to refuse otherwise — verbatim:

> "Answer the user's question using ONLY the information in the provided context
> below. ... Use only facts stated in the context. Do not add information from
> your own general knowledge. If the context does not contain enough information
> to answer, reply exactly: *'I don't have enough information on that.'* When
> sources disagree, say so rather than picking one side."

Generation uses Groq `llama-3.3-70b-versatile` at `temperature=0.2` to keep
answers tight to the retrieved text. The retrieved chunks are numbered and
labeled with their source file before being passed in, so the model sees which
document each fact came from.

**How source attribution is surfaced in the response:** Sources are built
**programmatically from retrieval metadata**, not generated by the LLM. After
`ask()` retrieves the top-k chunks, it collects their `source` filenames
(de-duplicated, order preserved) and returns them alongside the answer. This
guarantees the cited sources reflect what was actually retrieved, rather than
trusting the model to cite honestly.

---

## Retrieval Test Results

Three evaluation queries, with the top retrieved chunks and cosine distances
(lower = more similar). All top hits scored well below the 0.5 weak-match
threshold.

**Query: "How much do Vanderbilt students pay per meal on the meal plan?"**
| Source | Chunk | Distance |
|--------|-------|----------|
| political_review_mealplan.txt | #4 | 0.175 |
| political_review_mealplan.txt | #7 | 0.265 |
| political_review_mealplan.txt | #5 | 0.294 |

*Why relevant:* All three are from the meal-plan cost article, and the #1 hit is
the exact chunk containing "$2.42 per meal... freshmen pay $7.42/meal." The query
shares almost no keywords with "$2.42" — semantic search matched on meaning
(cost/price/per-meal), which is the point of embeddings.

**Query: "What is the difference between residential and retail dining?"**
| Source | Chunk | Distance |
|--------|-------|----------|
| business_review_aycte_vs_retail.txt | #7 | 0.115 |
| business_review_aycte_vs_retail.txt | #8 | 0.243 |
| business_review_aycte_vs_retail.txt | #0 | 0.277 |

*Why relevant:* All from the one document that directly contrasts the two dining
types, with the lowest distance in the whole test set (0.115) — the query maps
almost exactly onto that article's thesis.

**Query: "What new meal swipe limit did Campus Dining add and at which locations?"**
| Source | Chunk | Distance |
|--------|-------|----------|
| hustler_dining_changes_2026.txt | #0 | 0.226 |
| reddit_mealplan_thread.txt | #6 | 0.236 |
| hustler_dining_changes_2026.txt | #10 | 0.269 |

*(See Q4 below — relevant chunks were retrieved, but the one listing all five
affected locations was not in the top-5, which limited the answer.)*

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which dining hall did the Hustler rank #1 overall, and what specific item is given as a reason? | Rand Dining Center; **Rand cookies** ("best snack on campus") | "Rand is the top dining hall... reason: *'this delicious dessert.'*" Correct hall, but couldn't name the cookies. | Partially relevant | **Partially accurate** |
| 2 | What do Vanderbilt freshmen pay per meal vs. the average American, and what premium? | Freshmen $7.42/meal vs. avg $2.42/meal; up to ~394% premium | "$7.42 vs. $2.42... a 394% premium" (also computed 307% itself) | Relevant | **Accurate** |
| 3 | Difference between Residential and Retail Dining, and which is seen as higher quality? | Residential = all-you-care-to-eat; Retail = one entrée+side+drink; students see Retail as higher quality | Stated all three correctly | Relevant | **Accurate** |
| 4 | What three-swipe-per-day limit did Campus Dining add in 2026, and at which locations? | 3 swipes/day at Suzie's, Wasabi, VandyBlenz, Holy Smokes, Grins | "added at **Suzie's** locations" — missed the other four | Partially relevant | **Partially accurate** |
| 5 | Which dining hall do students say has the worst / lowest-quality food? | Kissam ("food quality is pretty bad... overcook") | "I don't have enough information on that." | Off-target | **Inaccurate** |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 2 accurate, 2 partially accurate, 1 inaccurate. Both partials and
the failure trace to *retrieval*, not generation — the model answered faithfully
from whatever context it was handed.

---

## Failure Case Analysis

**Question that failed:** Q5 — "Which dining hall do students say has the worst
or lowest-quality food?"

**What the system returned:** "I don't have enough information on that." — even
though the answer is in the corpus: a Reddit comment in
`reddit_dining_hall_thread.txt` (chunk #2) states *"kissam: overall food quality
is pretty bad, more misses than hits. they always manage to overcook their shit
to oblivion."*

**Root cause (tied to a specific pipeline stage): retrieval / embedding.** The
chunk containing the Kissam verdict was **never retrieved** into the top-5. The
query uses formal vocabulary ("worst," "lowest-quality"), while the relevant
chunk is short, slangy Reddit text ("overcook their shit to oblivion"). The
`all-MiniLM-L6-v2` embedding placed that informal phrasing far from the formal
query in vector space, so retrieval surfaced general "quality vs. quantity"
discussion chunks instead. With the actual evidence absent from its context, the
model did the correct thing given its instructions and refused. So the *refusal
logic worked*; the *system result is inaccurate* because the failure happened one
stage upstream, in retrieval.

**What you would change to fix it:** (1) Add **hybrid search** — combine semantic
search with BM25 keyword search so a literal match on "kissam"/"quality"/"worst"
can rescue chunks that embed poorly. (2) Use a stronger embedding model less
sensitive to register/slang. (3) Increase top-k, accepting more context dilution
as a tradeoff.

**Second documented case (Q1, partial) — chunk boundary.** The system named the
right hall (Rand) but said the reason was "this delicious dessert" instead of
"Rand cookies." The source reads *"Rand cookies are easily the best snack...
With this delicious dessert in its arsenal, Rand is the top dining hall."* The
chunk split separated "Rand cookies" from the "this delicious dessert → #1"
sentence, so the model retrieved the pronoun without its antecedent. A larger
overlap (or paragraph-level chunking for the ranking article) would keep the
noun and its reference together.

*(Note on query sensitivity: during development, the vaguer phrasing "which
dining hall is ranked best?" returned **Zeppos** — citing a Reddit user's
informal ranking — while the precise eval wording "Hustler rank #1" returned
**Rand**. Identical system; query phrasing alone flipped which "ranking" chunk
won retrieval.)*

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the Chunking
Strategy and Retrieval Approach sections in `planning.md` before coding meant
each implementation step had a concrete target — ~600-char paragraph-aware
chunks, `all-MiniLM-L6-v2`, ChromaDB with source metadata. When generating the
ingestion and embedding code, the spec sections served directly as the prompt,
so the output matched the intended design instead of being generic. The
"Anticipated Challenges" section also predicted the exact failures that later
showed up (conflicting sources, boundary-split facts), which made them faster to
recognize and explain during evaluation.

**One way your implementation diverged from the spec, and why:** The spec
specified **top-k = 4**, but after seeing retrieval results I changed it to
**top-k = 5**. During the Milestone 4/5 tests, the explicit "#1 ranked hall"
chunk for Q1 wasn't making the top-4, which produced vague answers. Raising k to
5 gave generation more of the relevant context without noticeably diluting it.
This is exactly the kind of tuning the spec anticipated ("I'll tune this after
I've seen real results"), so the divergence was a planned refinement rather than
an abandonment of the design.

---

## AI Usage

I used **Claude (Claude Code)** as my primary AI tool throughout, feeding it the
relevant `planning.md` sections and reviewing/correcting its output at each step.

**Instance 1 — Ingestion and chunking**

- *What I gave the AI:* My Documents and Chunking Strategy sections (10 `.txt`
  files mixing long articles and short Reddit threads; ~600-char paragraph-aware
  chunks with 100-char overlap), plus a note that the files contained a UTF-8 BOM
  and trailing author-bio boilerplate.
- *What it produced:* `ingest.py` — a loader + `clean_text()` + a paragraph-aware
  `chunk_text()` writing `chunks.json` with source metadata.
- *What I changed or overrode:* After inspecting the output I confirmed the chunk
  count (150) was in range and verified 5 sample chunks were clean and
  self-contained, rather than trusting the script blindly. I kept the
  character-based overlap even though it occasionally starts a chunk mid-sentence,
  after deciding it didn't hurt retrieval — a tradeoff I noted rather than
  over-engineering around.

**Instance 2 — Retrieval tuning and failure analysis**

- *What I gave the AI:* My Retrieval Approach section (`all-MiniLM-L6-v2`,
  ChromaDB, top-k) and my 5 evaluation questions.
- *What it produced:* `embed.py` (embedding + `retrieve()`) and a run of all 5
  questions through the pipeline with distances and retrieved chunks.
- *What I changed or overrode:* I **overrode the spec's top-k from 4 to 5** after
  the Q1 retrieval missed the "#1 ranked hall" chunk. I also rejected the surface
  reading that Q5's refusal meant the system "worked" — by inspecting which chunks
  were retrieved, I traced the failure to an embedding/retrieval miss (the Kissam
  verdict chunk never surfaced), which became the documented failure case rather
  than being hidden.

---

## Query Interface

A **Gradio** web UI (`app.py`, `python app.py` → http://localhost:7860).

- **Input:** a single text box ("Your question") with an Ask button; pressing
  Enter also submits. Four clickable example questions are provided.
- **Output:** an "Answer" box (the grounded response) and a "Retrieved from" box
  listing the source documents the answer drew from.

**Sample interaction transcript:**

```
Your question:  What is the difference between residential and retail dining?

Answer:  Residential Dining Halls are "all-you-can-eat" (one swipe, eat as much
as you like), while Retail Dining limits you to an entree, side, and drink per
swipe. Students perceive Retail Dining as higher quality, while Residential
Dining Halls offer more variety and the freedom of all-you-can-eat but are seen
as lesser in quality.

Retrieved from:
• business_review_aycte_vs_retail.txt
• hustler_campus_dining_review.txt
```

**Out-of-scope example (grounding guardrail):**

```
Your question:  What do students say about parking near the football stadium?

Answer:  I don't have enough information on that.
```
