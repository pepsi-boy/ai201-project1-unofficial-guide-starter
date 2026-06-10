"""
Milestone 5: Grounded response generation.

Wires retrieval (embed.py) to the Groq LLM. The system prompt forces the
model to answer ONLY from the retrieved chunks and to refuse when they don't
cover the question. Sources are attached programmatically (not left to the
LLM) so every answer is attributable.

    from query import ask
    result = ask("Which dining hall is ranked best?")
    print(result["answer"], result["sources"])
"""

import os

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5  # bumped from 4 so the explicit "#1 ranked hall" chunk is included

# Map internal filenames to human-readable source names for citations.
SOURCE_NAMES = {
    "hustler_dining_ranking.txt":
        'The Vanderbilt Hustler — "A ranking of Vanderbilt\'s dining options"',
    "hustler_campus_dining_review.txt":
        'The Vanderbilt Hustler — "Lots of change, some progress: A review of Campus Dining"',
    "hustler_vandycart_reviews.txt":
        'The Vanderbilt Hustler — "Student reviews of VandyCart"',
    "hustler_dining_losses.txt":
        'The Vanderbilt Hustler — "3 years of Campus Dining losses, ranked"',
    "hustler_mealplan_feedback.txt":
        'The Vanderbilt Hustler — "Dining introduces updated meal plan options"',
    "hustler_dining_changes_2026.txt":
        'The Vanderbilt Hustler — "Campus Dining implements changes to several dining locations"',
    "political_review_mealplan.txt":
        'Vanderbilt Political Review — "Is the Vanderbilt Meal Plan Worth It?"',
    "business_review_aycte_vs_retail.txt":
        'Vanderbilt Business Review — "Dining Halls: All You Care to Eat vs Retail Dining"',
    "reddit_dining_hall_thread.txt":
        "Reddit r/Vanderbilt — dining hall quality thread",
    "reddit_mealplan_thread.txt":
        "Reddit r/Vanderbilt — meal plan / dining failures thread",
}


def source_name(filename):
    """Human-readable citation for a source file (falls back to the filename)."""
    return SOURCE_NAMES.get(filename, filename)

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are The Unofficial Guide to Vanderbilt dining. \
Answer the user's question using ONLY the information in the provided context \
below. The context is made of excerpts from student reviews, the student \
newspaper, and Reddit threads.

Rules:
- Use only facts stated in the context. Do not add information from your own \
general knowledge.
- If the context does not contain enough information to answer, reply exactly: \
"I don't have enough information on that."
- When sources disagree, say so rather than picking one side.
- Be concise and specific. Quote concrete details (names, numbers, ratings) \
when the context provides them."""


def _format_context(hits):
    """Number each retrieved chunk and label it with its source file."""
    blocks = []
    for i, hit in enumerate(hits, 1):
        blocks.append(f"[{i}] (source: {source_name(hit['source'])})\n{hit['text']}")
    return "\n\n".join(blocks)


def ask(question, k=TOP_K):
    """Retrieve context, generate a grounded answer, and attach sources."""
    hits = retrieve(question, k=k)
    context = _format_context(hits)

    response = _client.chat.completions.create(
        model=MODEL,
        temperature=0.2,  # low: keep answers tight to the context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Source attribution is built from retrieval metadata, not the LLM, so it
    # is guaranteed to reflect what was actually retrieved. De-dup, keep order,
    # and map to human-readable source names.
    sources = list(dict.fromkeys(source_name(hit["source"]) for hit in hits))

    return {"answer": answer, "sources": sources, "hits": hits}


if __name__ == "__main__":
    # Quick end-to-end smoke test, including an out-of-scope question.
    for q in [
        "Which dining hall is ranked the best and why?",
        "What do students say about parking near the football stadium?",
    ]:
        print("\n" + "=" * 75)
        print("Q:", q)
        result = ask(q)
        print("\nANSWER:", result["answer"])
        print("\nSOURCES:", ", ".join(result["sources"]))
