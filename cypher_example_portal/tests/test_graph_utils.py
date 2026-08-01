from src.graph_utils import (
    does_question_exist,
    fetch_most_similar_question,
    is_valid_cypher_query,
)


def test_does_question_exist() -> None:
    does_question_exist("Example question")


def test_is_valid_cypher_query() -> None:
    bad_query = "Not a real query"

    assert is_valid_cypher_query(bad_query) is False


def test_fetch_most_similar_question() -> None:
    fetch_most_similar_question("example")
