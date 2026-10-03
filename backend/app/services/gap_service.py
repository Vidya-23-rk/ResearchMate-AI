import json
from typing import Any, Dict, List

from app.services.paper_details_service import paper_details_service
from app.services.llm_service import llm_service


class GapService:

    def detect_gaps(
        self,
        paper_ids: List[str]
    ) -> List[str]:
        if not paper_ids:
            return []

        import time
        papers = []
        for paper_id in paper_ids:
            try:
                papers.append(paper_details_service.get_paper_details(paper_id))
                time.sleep(1.2)  # Avoid Semantic Scholar rate limit
            except Exception:
                continue

        if not papers:
            return []

        # Construct a combined prompt for the LLM
        abstracts_text = ""
        for i, paper in enumerate(papers, 1):
            abstract = paper.get("abstract") or "No abstract available."
            title = paper.get("title") or "Untitled"
            abstracts_text += f"\n--- Paper {i} ---\nTitle: {title}\nAbstract: {abstract}\n"

        prompt = f"""
You are an expert academic research director.
I am providing you with the titles and abstracts of {len(papers)} related research papers.

Analyze these papers collectively to identify RECURRING limitations and global research gaps.
Then, synthesize these gaps into 3 to 5 highly specific "Potential research opportunities".

Your output must be ONLY a valid JSON list of strings representing the opportunities.

Example Output:
[
  "Cross-dataset generalization for real-world application scenarios",
  "Lightweight architectures for edge-device deployment",
  "Explainable models for interpreting internal state dynamics"
]

Here are the papers:
{abstracts_text}
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
            result = self._parse_json_response(response.text)
            if isinstance(result, list):
                return [str(x) for x in result]
            return []
        except (ValueError, TypeError, json.JSONDecodeError):
            return []

    @staticmethod
    def _parse_json_response(response_text: str) -> Any:
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)


gap_service = GapService()
