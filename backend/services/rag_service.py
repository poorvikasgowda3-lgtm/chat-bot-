import logging
from typing import List, Dict, Any
from backend.config import settings
from backend.models.schemas import QuestionResponse, SourceCitation
from backend.services.embedding_service import embedding_service
from backend.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.llm_model = settings.LLM_MODEL
        self.openai_key = settings.OPENAI_API_KEY

    def answer_question(self, question: str, top_k: int = 3) -> QuestionResponse:
        # 1. Embed user question
        question_vector = embedding_service.generate_embeddings([question])[0]

        # 2. Search Qdrant for top relevant chunks
        search_results = qdrant_service.search_similar(question_vector, top_k=top_k)

        if not search_results:
            return QuestionResponse(
                question=question,
                answer="No relevant documents found in the vector database. Please upload a PDF first.",
                sources=[],
                found_in_doc=False
            )

        # 3. Construct context & citations
        context_blocks = []
        citations: List[SourceCitation] = []

        for idx, item in enumerate(search_results):
            payload = item["payload"]
            score = item["score"]
            text_snippet = payload.get("text", "")
            page_num = payload.get("page_number", 0)
            filename = payload.get("pdf_filename", "Unknown")
            chunk_id = payload.get("chunk_id", "")

            context_blocks.append(f"[Source {idx+1} | Page {page_num} | File: {filename}]:\n{text_snippet}")
            citations.append(SourceCitation(
                pdf_filename=filename,
                page_number=page_num,
                chunk_id=chunk_id,
                text_snippet=text_snippet,
                score=round(score, 4)
            ))

        context_str = "\n\n".join(context_blocks)

        # 4. Generate answer via OpenAI or local fallback synthesizer
        answer, found_in_doc = self._generate_llm_response(question, context_str)

        return QuestionResponse(
            question=question,
            answer=answer,
            sources=citations,
            found_in_doc=found_in_doc
        )

    def _generate_llm_response(self, question: str, context: str) -> (str, bool):
        system_prompt = (
            "You are a helpful and precise assistant that answers user questions based strictly on the provided PDF document context.\n"
            "Rules:\n"
            "1. Base your answer strictly on the context provided below.\n"
            "2. If the answer cannot be found or inferred from the context, clearly state: 'The requested information could not be found in the provided PDF document.'\n"
            "3. Include relevant page numbers or details mentioned in the text when applicable.\n"
            "4. Do not make up information."
        )

        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2
                )
                ans = response.choices[0].message.content.strip()
                found = "could not be found" not in ans.lower()
                return ans, found
            except Exception as e:
                logger.error(f"OpenAI completion error: {e}. Using fallback contextual answer generation.")

        # Fallback local synthesis if no OpenAI API key provided
        return self._local_fallback_synthesis(question, context)

    def _local_fallback_synthesis(self, question: str, context: str) -> (str, bool):
        """Intelligent local synthesis using extracted vector context when OpenAI API key is not present."""
        keywords = [w.lower() for w in question.split() if len(w) > 3]
        
        # Check if context matches any question keywords
        matches = [line for line in context.split("\n") if any(kw in line.lower() for kw in keywords)]

        if matches:
            summary = "\n".join(matches[:4])
            ans = f"Based on the uploaded document context:\n\n{summary}\n\n*(Note: Add your OPENAI_API_KEY to .env for full AI natural language synthesis)*"
            return ans, True
        else:
            ans = "The requested information could not be found in the provided PDF document context."
            return ans, False

rag_service = RAGService()
