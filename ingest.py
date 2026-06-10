"""
Milestone 3: Document ingestion and chunking.

Loads every .txt file in documents/, cleans it (strips the UTF-8 BOM,
author bios, and Reddit vote/UI artifacts), then splits it into
paragraph-aware chunks (~600 chars, ~100 char overlap) tagged with their
source filename. Writes the result to chunks.json for the embedding step.
"""

import json
import os
import re

DOCUMENTS_DIR = "documents"
OUTPUT_FILE = "chunks.json"

CHUNK_SIZE = 600   # target characters per chunk
OVERLAP = 100      # characters carried over between adjacent chunks


def clean_text(text):
    """Remove boilerplate that isn't part of the substantive content."""
    # 1. Strip the UTF-8 BOM that copy-paste left at the start of each file.
    text = text.replace("﻿", "")

    # 2. Drop trailing author bios — everything from "About the Contributors" on.
    text = re.split(r"About the Contributors?", text)[0]

    # 3. Remove Reddit UI artifacts and other line-level junk.
    junk_lines = {"Upvote", "Downvote", "Go to comments", "Tags:"}
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in junk_lines:
            continue
        if stripped.isdigit():          # vote counts like "7" / "5"
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    # 4. Collapse runs of blank lines and trim trailing whitespace per line.
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def split_sentences(paragraph):
    """Split an over-long paragraph on sentence boundaries (. ! ?)."""
    parts = re.split(r"(?<=[.!?])\s+", paragraph)
    return [p.strip() for p in parts if p.strip()]


def overlap_tail(chunk, overlap=OVERLAP):
    """Return the last ~overlap chars of a chunk, starting at a word boundary."""
    if len(chunk) <= overlap:
        return chunk
    tail = chunk[-overlap:]
    space = tail.find(" ")
    return tail[space + 1:] if space != -1 else tail


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Greedily pack paragraphs into ~chunk_size chunks with overlap.

    Splits on paragraph boundaries first so we never cut mid-thought; only
    falls back to sentence splitting when a single paragraph is too long.
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current = ""

    def flush():
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
            current = overlap_tail(current)

    for para in paragraphs:
        units = [para] if len(para) <= chunk_size else split_sentences(para)
        for unit in units:
            # +1 accounts for the joining space.
            if current and len(current) + len(unit) + 1 > chunk_size:
                flush()
            current = (current + " " + unit).strip() if current else unit

    if current.strip():
        chunks.append(current.strip())

    return chunks


def main():
    all_chunks = []
    per_doc_counts = {}

    filenames = sorted(f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".txt"))
    for filename in filenames:
        path = os.path.join(DOCUMENTS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        text = clean_text(raw)
        chunks = chunk_text(text)
        per_doc_counts[filename] = len(chunks)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": filename,
                "chunk_index": i,
                "char_len": len(chunk),
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # --- Inspection output (Milestone 3 checkpoint) ---
    print(f"Loaded {len(filenames)} documents")
    print(f"Total chunks: {len(all_chunks)}\n")
    print("Chunks per document:")
    for filename, count in per_doc_counts.items():
        print(f"  {filename:45s} {count:3d}")

    print("\n5 sample chunks (spread across the corpus):")
    step = max(1, len(all_chunks) // 5)
    for chunk in all_chunks[::step][:5]:
        print("\n" + "-" * 70)
        print(f"source: {chunk['source']}  (chunk #{chunk['chunk_index']}, "
              f"{chunk['char_len']} chars)")
        print(chunk["text"])

    print(f"\nWrote {len(all_chunks)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
