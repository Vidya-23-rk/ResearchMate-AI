from app.services.llm_service import llm_service


class SummarizationService:

    def __init__(self, chunk_size: int = 12000):
        self.chunk_size = chunk_size

    def _split_text(self, text: str):
        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)

            if end < text_length:
                last_space = text.rfind(" ", start, end)

                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end

        return chunks

    def summarize_document(self, document_text: str):

        if not document_text or not document_text.strip():
            return {
                "success": False,
                "message": "No text available for summarization."
            }

        chunks = self._split_text(document_text)

        if not chunks:
            return {
                "success": False,
                "message": "No usable text found in the document."
            }

        partial_summaries = []

        # -----------------------------------------------------
        # Step 1 — Summarize each section of the document
        # -----------------------------------------------------

        for index, chunk in enumerate(chunks, start=1):

            prompt = f"""
You are an academic research assistant.

Analyze this section of a research paper.

Use ONLY the information explicitly present in the section.

Do NOT:
- invent information
- use outside knowledge
- assume missing details
- create unsupported numbers or claims

Extract useful information about:
- research problem
- objective
- methodology
- dataset
- key findings
- limitations
- conclusion

If something is not present, do not invent it.

DOCUMENT SECTION {index}:

{chunk}

Provide a concise factual summary of this section.
"""

            response = llm_service.client.models.generate_content(
                model=llm_service.model,
                contents=prompt
            )

            if response.text:
                partial_summaries.append(
                    response.text.strip()
                )

        if not partial_summaries:
            return {
                "success": False,
                "message": "Unable to generate a summary."
            }

        # -----------------------------------------------------
        # Step 2 — Combine partial summaries
        # -----------------------------------------------------

        combined_summary = "\n\n".join(
            partial_summaries
        )

        final_prompt = f"""
You are an academic research assistant.

Create a final structured summary of the research paper
using ONLY the information contained in the section summaries
provided below.

Do NOT use outside knowledge.
Do NOT invent information.
Do NOT assume missing details.

If information for a section is not available, write exactly:

"Not specified in the provided document."

Return EXACTLY these sections:

Research Problem:
Objective:
Methodology:
Dataset:
Key Findings:
Limitations:
Conclusion:

Keep each section concise but informative.

SECTION SUMMARIES:

{combined_summary}
"""

        final_response = llm_service.client.models.generate_content(
            model=llm_service.model,
            contents=final_prompt
        )

        if not final_response.text:
            return {
                "success": False,
                "message": "Unable to generate the final summary."
            }

        return {
            "success": True,
            "summary": final_response.text.strip()
        }


summarization_service = SummarizationService()