import json
from typing import Any, Dict, List

from app.services.paper_details_service import (
    paper_details_service
)
from app.services.llm_service import llm_service


class OpportunityService:

    def get_opportunities(
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
You are an academic research assistant.

Analyze the following research paper information
and identify research opportunities.

Use ONLY information explicitly present
in the provided paper information.

DO NOT:
- invent information
- assume missing information
- use outside knowledge
- claim that a research direction is definitely novel
- create unsupported results
- create unsupported limitations
- create unsupported future work
- invent page numbers
- invent section names

Identify the following where explicitly supported:

1. Limitations
2. Future work
3. Unresolved problems
4. Methodological gaps or differences
5. Potential research directions suggested by the paper

For every finding, provide supporting evidence.

The evidence excerpt MUST be copied directly
from the provided paper text.

Since the provided information is only an abstract,
page numbers and section names are not available.
Therefore:

- page_number MUST be null
- section MUST be null

Return ONLY valid JSON in exactly this format:

{{
    "opportunities": [
        {{
            "category": "Limitation",
            "statement": "...",
            "evidence": [
                {{
                    "page_number": null,
                    "section": null,
                    "excerpt": "Exact text copied from the paper."
                }}
            ]
        }}
    ]
}}

Allowed category values are:

- Limitation
- Future Work
- Unresolved Problem
- Methodological Gap
- Research Direction

If there is no explicitly supported opportunity,
return:

{{
    "opportunities": []
}}

PAPER TITLE:
{title}

PAPER ABSTRACT:
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

        opportunities = result.get(
            "opportunities",
            []
        )

        if not isinstance(opportunities, list):
            return []

        cleaned = []

        allowed_categories = {
            "Limitation",
            "Future Work",
            "Unresolved Problem",
            "Methodological Gap",
            "Research Direction"
        }

        for item in opportunities:

            if not isinstance(item, dict):
                continue

            category = item.get("category")
            statement = item.get("statement")
            evidence = item.get("evidence", [])

            if category not in allowed_categories:
                continue

            if not isinstance(statement, str):
                continue

            statement = statement.strip()

            if not statement:
                continue

            if not isinstance(evidence, list):
                evidence = []

            cleaned_evidence = []

            for evidence_item in evidence:

                if not isinstance(
                    evidence_item,
                    dict
                ):
                    continue

                page_number = evidence_item.get(
                    "page_number"
                )

                section = evidence_item.get(
                    "section"
                )

                excerpt = evidence_item.get(
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

                    if not isinstance(
                        section,
                        str
                    ):
                        section = None

                    else:
                        section = section.strip()

                        if not section:
                            section = None

                if not isinstance(
                    excerpt,
                    str
                ):
                    continue

                excerpt = excerpt.strip()

                if not excerpt:
                    continue

                cleaned_evidence.append({
                    "page_number": page_number,
                    "section": section,
                    "excerpt": excerpt
                })

            cleaned.append({
                "category": category,
                "statement": statement,
                "evidence": cleaned_evidence
            })

        return cleaned

    @staticmethod
    def _parse_json_response(
        response_text: str
    ) -> Dict[str, Any]:

        text = response_text.strip()

        if text.startswith("```"):

            lines = text.splitlines()

            if (
                lines
                and lines[0].startswith("```")
            ):
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            text = "\n".join(
                lines
            ).strip()

        return json.loads(text)


opportunity_service = OpportunityService()