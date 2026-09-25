from app.services.citation_service import citation_service


def test_citation_with_missing_metadata():

    paper = {
        "paper_id": "TEST001",
        "title": "AI Research Study",
        "authors": [],
        "year": None,
        "doi": None,
        "venue": None,
        "url": None
    }

    citations = citation_service.generate_citations(
        paper
    )

    assert "AI Research Study" in citations["apa"]
    assert "AI Research Study" in citations["ieee"]
    assert "AI Research Study" in citations["mla"]

    assert "Author not available" in citations["apa"]
    assert "Author not available" in citations["ieee"]

    assert "n.d." in citations["apa"]

    assert "https://doi.org/" not in citations["apa"]
    assert "doi:" not in citations["ieee"]