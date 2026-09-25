from google import genai

from app.config import settings


class LLMService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.llm_api_key
        )

        self.model = "gemini-3.5-flash-lite"

    # =========================================================
    # PHASE 4 — DOCUMENT QUESTION ANSWERING
    # =========================================================

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

    # =========================================================
    # PHASE 5 — DOCUMENT SUMMARIZATION
    # =========================================================

    def generate_summary(
        self,
        document_text: str
    ):
        if not document_text or not document_text.strip():
            return {
                "research_problem": "Not available in the document.",
                "objective": "Not available in the document.",
                "methodology": "Not available in the document.",
                "dataset": "Not available in the document.",
                "key_findings": "Not available in the document.",
                "limitations": "Not available in the document.",
                "conclusion": "Not available in the document."
            }

        prompt = f"""
You are an academic research assistant.

Analyze the academic paper provided below.

Create a structured summary using ONLY information explicitly
supported by the paper.

DO NOT:
- use outside knowledge
- invent information
- assume missing details
- create fake datasets, methods, results, authors, or numbers

If a section is not clearly available in the paper, write:

"Not available in the document."

Return the summary using exactly these sections:

Research Problem:
Objective:
Methodology:
Dataset:
Key Findings:
Limitations:
Conclusion:

Keep each section concise but informative.

ACADEMIC PAPER:
{document_text}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        summary_text = response.text.strip()

        return self._parse_summary(summary_text)

    # =========================================================
    # PHASE 5 — SUMMARY PARSER
    # =========================================================

    def _parse_summary(self, summary_text: str):

        sections = {
            "research_problem": "Not available in the document.",
            "objective": "Not available in the document.",
            "methodology": "Not available in the document.",
            "dataset": "Not available in the document.",
            "key_findings": "Not available in the document.",
            "limitations": "Not available in the document.",
            "conclusion": "Not available in the document."
        }

        current_section = None

        section_mapping = {
            "Research Problem": "research_problem",
            "Objective": "objective",
            "Methodology": "methodology",
            "Dataset": "dataset",
            "Key Findings": "key_findings",
            "Limitations": "limitations",
            "Conclusion": "conclusion"
        }

        for line in summary_text.splitlines():

            line = line.strip()

            if not line:
                continue

            matched_section = False

            for title, key in section_mapping.items():

                if line.lower().startswith(title.lower() + ":"):
                    current_section = key

                    content = line.split(":", 1)[1].strip()

                    if content:
                        sections[key] = content

                    matched_section = True
                    break

            if matched_section:
                continue

            if current_section:
                if sections[current_section] == "Not available in the document.":
                    sections[current_section] = line
                else:
                    sections[current_section] += " " + line

        return sections


llm_service = LLMService()