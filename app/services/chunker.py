import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass(slots=True)
class Chunk:
    id: str
    text: str
    index: int

class RecursiveChunker:
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200, 
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ".", " ", ""]

    def split_text(self, text: str) -> List[str]:
        final_chunks = []
        self._split_text_recursive(text, self.separators, final_chunks)
        return final_chunks

    def _split_text_recursive(self, text: str, separators: List[str], final_chunks: List[str]):
        """
        Recursively splits text by the first separator that produces chunks smaller than chunk_size.
        """
        # Base case: text is small enough
        if len(text) <= self.chunk_size:
            final_chunks.append(text)
            return

        # Use the first separator in the list
        separator = separators[0]
        # If we run out of separators (hitting empty string), just force split
        if separator == "":
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                final_chunks.append(text[i : i + self.chunk_size])
            return

        # Attempt to split
        splits = text.split(separator)
        
        # Merge splits back into chunks
        current_doc = []
        current_length = 0
        for s in splits:
            s_len = len(s)
            if current_length + s_len + len(separator) > self.chunk_size:
                # If checking next layer of separators makes sense
                if len(separators) > 1:
                     # Recurse on the current buffer if it's too big? 
                     # Actually better strategy: if a SINGLE split is too big, recurse on IT. 
                     # If the buffer is too big, emit it (but we built it up so it should fit?)
                     
                     # Simple logic: emit current buffer
                     if current_doc:
                         doc = separator.join(current_doc)
                         if len(doc) > self.chunk_size:
                             # Recurse on this doc with next separator
                             self._split_text_recursive(doc, separators[1:], final_chunks)
                         else:
                             final_chunks.append(doc)
                     
                     current_doc = []
                     current_length = 0

            current_doc.append(s)
            current_length += s_len + len(separator)
            
        # Process remaining
        if current_doc:
            doc = separator.join(current_doc)
            if len(doc) > self.chunk_size and len(separators) > 1:
                self._split_text_recursive(doc, separators[1:], final_chunks)
            else:
                final_chunks.append(doc)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        # Improved logic for merging considering overlap (simplified here for robustness)
        # For a production grade, we'd use LangChain's logic. 
        # Here we implement a simpler "greedy merge"
        docs = []
        current_doc = []
        total = 0
        for d in splits:
            _len = len(d)
            if total + _len + len(separator) > self.chunk_size:
                if total > self.chunk_size:
                     pass # Handled by recursion usually
                if current_doc:
                    doc = separator.join(current_doc)
                    docs.append(doc)
                    # Handle Overlap: keep last few items? 
                    # Overlap is tricky in simple merge.
                    # We will stick to simple merge for now to avoid bugs, 
                    # as true overlap requires token counting or char slicing.
                    
                    # Simple overlap attempt: keep last element if small
                    while total > self.chunk_overlap and current_doc:
                         popped = current_doc.pop(0)
                         total -= (len(popped) + len(separator))
                    
                else: 
                     # Single item bigger than chunk_size
                     docs.append(d) 

            current_doc.append(d)
            total += _len + len(separator)
            
        if current_doc:
            docs.append(separator.join(current_doc))
        return docs


# Helper function to maintain backward compatibility
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Chunk]:
    # Simplified Recursive logic for stability
    # Using a known pattern: Split by largest separator, then merge.
    
    separators = ["\n\n", "\n", ". ", " ", ""]
    final_text_chunks = []
    
    def _split(text, seps):
        if not seps or len(text) <= chunk_size:
            return [text]
        
        sep = seps[0]
        if sep == "":
             return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-chunk_overlap)]
             
        parts = text.split(sep)
        chunks = []
        current = []
        current_len = 0
        
        for part in parts:
             # If a single part is huge, recurse on it
             if len(part) > chunk_size:
                 if current:
                     chunks.append(sep.join(current))
                     current = []
                     current_len = 0
                 # Recurse
                 sub_chunks = _split(part, seps[1:])
                 chunks.extend(sub_chunks)
                 continue
                 
             if current_len + len(part) + len(sep) > chunk_size:
                 chunks.append(sep.join(current))
                 
                 # Apply overlap: keep last N chars approx?
                 # Easier: keep last K parts that fit in overlap size
                 backtrack = []
                 backtrack_len = 0
                 for p in reversed(current):
                     if backtrack_len + len(p) + len(sep) < chunk_overlap:
                         backtrack.insert(0, p)
                         backtrack_len += len(p) + len(sep)
                     else:
                         break
                 current = backtrack
                 current_len = backtrack_len
                 
             current.append(part)
             current_len += len(part) + len(sep)
             
        if current:
            chunks.append(sep.join(current))
            
        return chunks

    final_text_chunks = _split(text, separators)
    
    # Wrap in Chunk objects
    return [
        Chunk(id=f"chunk_{i}", text=ct.strip(), index=i)
        for i, ct in enumerate(final_text_chunks)
        if ct.strip()
    ]