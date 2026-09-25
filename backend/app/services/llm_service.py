from google import genai

from app.config import settings


class LLMService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.llm_api_key
        )

        self.model = "gemini-3.5-flash-lite"

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: list[dict]
    ):
        if not retrieved_chunks:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in the uploaded document to answer this question."
                ),
                "sources": []
            }

        context_parts = []

        for chunk in retrieved_chunks:

            context_parts.append(
                f"""
Page {chunk['page_number']}

Evidence:
{chunk['text']}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
You are an academic research assistant.

Answer the user's question using ONLY the evidence provided below.

Do not use outside knowledge.
Do not invent facts.
Do not make assumptions that are not supported by the evidence.

If the evidence does not contain enough information to answer the
question, clearly say that the answer is not available in the
provided document.

Always keep the answer grounded in the supplied evidence.

USER QUESTION:
{question}

DOCUMENT EVIDENCE:
{context}

Provide a concise and accurate answer.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        answer = response.text.strip()

        sources = []

        for chunk in retrieved_chunks:
            sources.append(
                {
                    "page_number": chunk["page_number"],
                    "excerpt": chunk["text"][:500],
                    "score": chunk["score"]
                }
            )

        return {
            "answer": answer,
            "sources": sources
        }


llm_service = LLMService()