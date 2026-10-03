from app.services.retrieval_service import retrieval_service


DOCUMENT_ID = "7bc80a82-5dfb-47e5-a599-02491274e969"


def test_relevant_question_retrieves_chunks():
    results = retrieval_service.retrieve(
        document_id=DOCUMENT_ID,
        question="What is MLOPS?",
        top_k=5
    )

    assert len(results) > 0


def test_unsupported_question_returns_no_chunks():
    results = retrieval_service.retrieve(
        document_id=DOCUMENT_ID,
        question="What is the salary of the college principal?",
        top_k=5
    )

    assert len(results) == 0


def test_retrieved_chunks_have_source_metadata():
    results = retrieval_service.retrieve(
        document_id=DOCUMENT_ID,
        question="What is MLOPS?",
        top_k=5
    )

    assert len(results) > 0

    for result in results:
        assert "page_number" in result
        assert "text" in result
        assert "score" in result
        assert result["page_number"] > 0
        assert result["text"].strip()