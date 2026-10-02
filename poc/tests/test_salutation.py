"""A1: the salutation must contain exactly one honorific, never doubled."""

import pytest

from normalize import NAME_FORMAT_WARNING, format_salutation, salutation


def test_name_already_starting_with_khun_is_kept():
    assert salutation("คุณสมชาย ใจดี") == "คุณสมชาย ใจดี"


def test_plain_name_gets_khun_prefix():
    assert salutation("สมชาย ใจดี") == "คุณสมชาย ใจดี"


def test_surrounding_and_repeated_whitespace_is_cleaned():
    assert salutation("  สมชาย   ใจดี \n") == "คุณสมชาย ใจดี"


@pytest.mark.parametrize(
    "name",
    [
        "นายสมชาย ใจดี", "นาย สมชาย ใจดี", "นางสาวสมหญิง รักดี", "นางสมศรี",
        "ดร.สมชาย", "Dr. John Smith", "dr. john", "Mrs. Jane Doe",
    ],
)
def test_known_titles_do_not_get_khun(name):
    assert salutation(name) == " ".join(name.split())


def test_result_never_contains_doubled_khun():
    for name in ["คุณสมชาย", "สมชาย", "คุณ สมชาย"]:
        assert "คุณ คุณ" not in salutation(name)
        assert "คุณคุณ" not in salutation(name)


@pytest.mark.parametrize("name", ["สมชาย 123", "somchai@example.com", "สมชาย <b>x</b>"])
def test_unknown_format_is_kept_as_is_with_warning(name):
    result = format_salutation(name)
    assert result.text == " ".join(name.split())
    assert result.warning == NAME_FORMAT_WARNING


def test_known_format_has_no_warning():
    assert format_salutation("สมชาย ใจดี").warning is None


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        salutation("   ")


def test_latin_name_gets_khun_with_a_space():
    assert salutation("John Smith") == "คุณ John Smith"


def test_thai_name_gets_khun_without_a_space():
    assert salutation("สมชาย ใจดี") == "คุณสมชาย ใจดี"
