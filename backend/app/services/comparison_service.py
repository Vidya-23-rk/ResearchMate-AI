import json
from typing import Any, Dict, List

from app.services.paper_details_service import paper_details_service
from app.services.llm_service import llm_service


class ComparisonService:

    def compare_papers(
        self,
        paper_ids: List[str]
    ) -> List[Dict[str, Any]]:
        comparison = []

        for paper_id in paper_ids:
            paper = paper_details_service.get_paper_details(
                paper_id
            )

            authors = [
                author.get("name", "")
                for author in paper.get("authors", [])
                if author.get("name")
            ]

            extracted = self._extract_research_fields(
                paper
            )

            comparison.append({
                "paper_id": paper.get(
                    "paper_id",
                    paper_id
                ),
                "title": paper.get(
                    "title",
                    "Title not available"
                ),
                "authors": authors,
                "year": paper.get("year"),
                "problem": extracted["problem"],
                "methodology": extracted["methodology"],
                "dataset": extracted["dataset"],
                "results": extracted["results"],
                "limitations": extracted["limitations"]
            })

        return comparison

    def _extract_research_fields(
        self,
        paper: Dict[str, Any]
    ) -> Dict[str, str]:

        abstract = paper.get("abstract")

        if not abstract or not abstract.strip():
            return self._empty_fields()

        prompt = f"""
You are an academic research assistant.

Analyze the following research paper information.

Use ONLY the information explicitly present
in the provided text.

DO NOT:
- invent information
- assume missing information
- use outside knowledge
- create unsupported numbers
- guess the dataset
- guess the methodology
- guess results
- guess limitations

If a field is not explicitly available, return exactly:

"Not specified in the paper."

Extract these five fields:

1. problem
2. methodology
3. dataset
4. results
5. limitations

Return ONLY valid JSON in exactly this format:

{{
    "problem": "...",
    "methodology": "...",
    "dataset": "...",
    "results": "...",
    "limitations": "..."
}}

PAPER TITLE:
{paper.get("title", "Title not available")}

PAPER ABSTRACT:
{abstract}
"""

        try:
            response = llm_service.client.models.generate_content(
                model=llm_service.model,
                contents=prompt
            )
        except Exception:
            return self._empty_fields()

        if not response or not response.text:
            return self._empty_fields()

        try:
            result = self._parse_json_response(
                response.text
            )
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._empty_fields()

        return {
            "problem": self._clean_field(
                result.get("problem")
            ),
            "methodology": self._clean_field(
                result.get("methodology")
            ),
            "dataset": self._clean_field(
                result.get("dataset")
            ),
            "results": self._clean_field(
                result.get("results")
            ),
            "limitations": self._clean_field(
                result.get("limitations")
            )
        }

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

    @staticmethod
    def _clean_field(value: Any) -> str:

        if not isinstance(value, str):
            return "Not specified in the paper."

        value = value.strip()

        if not value:
            return "Not specified in the paper."

        return value

    @staticmethod
    def _empty_fields() -> Dict[str, str]:

        return {
            "problem": "Not specified in the paper.",
            "methodology": "Not specified in the paper.",
            "dataset": "Not specified in the paper.",
            "results": "Not specified in the paper.",
            "limitations": "Not specified in the paper."
        }


comparison_service = ComparisonService()