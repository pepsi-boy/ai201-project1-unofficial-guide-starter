"""
Milestone 5: Query interface.

A minimal Gradio web UI over the RAG pipeline. Enter a question, get a
grounded answer plus the source documents it was drawn from.

    python app.py   ->   http://localhost:7860
"""

import gradio as gr

from query import ask


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — Vanderbilt Dining") as demo:
    gr.Markdown(
        "# 🍽️ The Unofficial Guide — Vanderbilt Dining\n"
        "Ask about dining halls, meal plans, and campus food. Answers come "
        "only from student reviews, the Vanderbilt Hustler, and Reddit."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which dining hall is ranked the best?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    gr.Examples(
        examples=[
            "Which dining hall is ranked the best and why?",
            "How much do students pay per meal on the meal plan?",
            "What's the difference between residential and retail dining?",
            "Which dining hall do students say has the worst food?",
        ],
        inputs=inp,
    )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
