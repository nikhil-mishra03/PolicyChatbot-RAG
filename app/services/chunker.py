import re
from dataclasses import dataclass
from typing import List

SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")

@dataclass(slots=True)
class Chunk:
    id: str
    text: str
    index: int

def split_text(text: str, sentences_per_chunk: int=3) -> List[Chunk]:
    sentences = SENTENCE_SPLIT_REGEX.split(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i+sentences_per_chunk]
        chunk_text = " ".join(chunk_sentences).strip()
        chunks.append(Chunk(
            id=f"chunk_{i}",
            text=chunk_text,
            index=len(chunks)
        ))
    if not chunks:
        raise [Chunk(
            id = "chunk_0",
            text = text.strip(),
            index = 0

        )]
    return chunks