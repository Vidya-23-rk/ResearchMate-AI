import json
from typing import Any, Dict, List

from app.services.paper_details_service import (
    paper_details_service
)
from app.services.llm_service import llm_service


class EvidenceService:

    def get_evidence(
        self,
        paper_id: str
    ) -> List[Dict[str, Any]]:

        paper = paper_details_service.get_paper_details(
            paper_id
        )

        title = paper.get(
            "title",
            "Title not available"
        )

        abstract = paper.get("abstract")

        if not abstract or not abstract.strip():
            return []

        prompt = f"""
You are an academic evidence extraction assistant.

Extract evidence from the provided research paper
information.

IMPORTANT RULES:

- Use ONLY the provided text.
- Do not use outside knowledge.
- Do not invent evidence.
- Do not invent page numbers.
- Do not invent section names.
- Do not paraphrase the evidence excerpt.
- The excerpt must be copied directly from the
  provided text.
- If a page number is not available, return null.
- If a section is not explicitly identifiable,
  return null.

Return only evidence that is directly supported
by the provided text.

Return ONLY valid JSON in exactly this format:

{{
    "evidence": [
        {{
            "page_number": null,
            "section": null,
            "excerpt": "Exact text copied from the paper."
        }}
    ]
}}

PAPER TITLE:
{title}

PAPER TEXT:
{abstract}
"""

        try:
            response = llm_service.client.models.generate_content(
                model=llm_service.model,
                contents=prompt
            )
        except Exception:
            return []

        if not response or not response.text:
            return []

        try:
            result = self._parse_json_response(
                response.text
            )
        except (
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):
            return []

        evidence = result.get(
            "evidence",
            []
        )

        if not isinstance(evidence, list):
            return []

        cleaned = []

        for item in evidence:

            if not isinstance(item, dict):
                continue

            page_number = item.get(
                "page_number"
            )

            section = item.get(
                "section"
            )

            excerpt = item.get(
                "excerpt"
            )

            if page_number is not None:
                if (
                    not isinstance(
                        page_number,
                        int
                    )
                    or page_number < 1
                ):
                    page_number = None

            if section is not None:
                if not isinstance(section, str):
                    section = None
                else:
                    section = section.strip()

                    if not section:
                        section = None

            if not isinstance(excerpt, str):
                continue

            excerpt = excerpt.strip()

            if not excerpt:
                continue

            cleaned.append({
                "page_number": page_number,
                "section": section,
                "excerpt": excerpt
            })

        return cleaned

    @staticmethod
    def _parse_json_response(
        response_text: str
    ) -> Dict[str, Any]:

        text = response_text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        return json.loads(text)


evidence_service = EvidenceService()