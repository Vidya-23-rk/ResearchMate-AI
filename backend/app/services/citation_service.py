from typing import Any, Dict


class CitationService:

    def generate_citations(
        self,
        paper: Dict[str, Any]
    ) -> Dict[str, str]:

        return {
            "apa": self._format_apa(paper),
            "ieee": self._format_ieee(paper),
            "mla": self._format_mla(paper)
        }

    # =========================================================
    # AUTHOR FORMATTING
    # =========================================================

    def _get_authors(
        self,
        paper: Dict[str, Any]
    ):

        authors = paper.get("authors") or []

        return [
            author.get("name", "").strip()
            for author in authors
            if isinstance(author, dict)
            and author.get("name")
        ]

    # =========================================================
    # APA
    # =========================================================

    def _format_apa(
        self,
        paper: Dict[str, Any]
    ) -> str:

        authors = self._get_authors(paper)

        title = paper.get("title")
        year = paper.get("year")
        venue = paper.get("venue")
        doi = paper.get("doi")

        if not authors:
            author_text = "Author not available"
        elif len(authors) == 1:
            author_text = authors[0]
        elif len(authors) == 2:
            author_text = f"{authors[0]} & {authors[1]}"
        else:
            author_text = ", ".join(authors[:-1])
            author_text += f", & {authors[-1]}"

        year_text = (
            f"({year})."
            if year
            else "(n.d.)."
        )

        citation = (
            f"{author_text} {year_text} "
            f"{title or 'Title not available'}."
        )

        if venue:
            citation += f" {venue}."

        if doi:
            citation += f" https://doi.org/{doi}"

        return citation

    # =========================================================
    # IEEE
    # =========================================================

    def _format_ieee(
        self,
        paper: Dict[str, Any]
    ) -> str:

        authors = self._get_authors(paper)

        title = paper.get("title")
        venue = paper.get("venue")
        year = paper.get("year")
        doi = paper.get("doi")

        if authors:
            author_text = ", ".join(authors)
        else:
            author_text = "Author not available"

        citation = (
            f"{author_text}, "
            f"\"{title or 'Title not available'}\""
        )

        if venue:
            citation += f", {venue}"

        if year:
            citation += f", {year}"

        citation += "."

        if doi:
            citation += f" doi: {doi}."

        return citation

    # =========================================================
    # MLA
    # =========================================================

    def _format_mla(
        self,
        paper: Dict[str, Any]
    ) -> str:

        authors = self._get_authors(paper)

        title = paper.get("title")
        venue = paper.get("venue")
        year = paper.get("year")
        doi = paper.get("doi")

        if not authors:
            author_text = "Author not available."
        elif len(authors) == 1:
            author_text = f"{authors[0]}."
        else:
            author_text = f"{authors[0]}, et al."

        citation = (
            f"{author_text} "
            f"\"{title or 'Title not available'}.\""
        )

        if venue:
            citation += f" {venue},"

        if year:
            citation += f" {year}."

        if doi:
            citation += f" https://doi.org/{doi}."

        return citation


citation_service = CitationService()