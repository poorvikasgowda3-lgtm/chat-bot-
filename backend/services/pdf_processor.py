import io
import re
from typing import List, Dict, Any
from pypdf import PdfReader
from backend.models.schemas import DocumentChunk

class PDFProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        """Clean extracted PDF text by standardizing whitespace and removing null bytes."""
        if not text:
            return ""
        # Replace null bytes
        text = text.replace("\x00", "")
        # Replace multiple newlines / spaces with standard spacing
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def process_pdf(self, file_content: bytes, filename: str) -> List[DocumentChunk]:
        """Extract text page by page and split into overlapping chunks."""
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        chunks: List[DocumentChunk] = []
        chunk_counter = 0

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            raw_text = page.extract_text() or ""
            cleaned_page_text = self.clean_text(raw_text)

            if not cleaned_page_text:
                continue

            # Split text of page into words or character chunks with overlap
            page_chunks = self._chunk_text(cleaned_page_text)
            for chunk_str in page_chunks:
                chunk_counter += 1
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{filename}_p{page_num}_c{chunk_counter}",
                        pdf_filename=filename,
                        page_number=page_num,
                        text=chunk_str
                    )
                )

        return chunks

    def _chunk_text(self, text: str) -> List[str]:
        """Simple token/character aware overlap chunker."""
        words = text.split(' ')
        chunks = []
        
        current_chunk = []
        current_len = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1
            if current_len >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                # Step back for overlap
                overlap_words = []
                overlap_len = 0
                for w in reversed(current_chunk):
                    if overlap_len + len(w) + 1 <= self.chunk_overlap:
                        overlap_words.insert(0, w)
                        overlap_len += len(w) + 1
                    else:
                        break
                current_chunk = overlap_words
                current_len = overlap_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

pdf_processor = PDFProcessor()
