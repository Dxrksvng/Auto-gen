"""A2: the hospital name must not repeat the word 'โรงพยาบาล'."""

import pytest

from normalize import hospital


@pytest.mark.parametrize(
    "name",
    ["โรงพยาบาลกรุงเทพ", "รพ.รามาธิบดี", "ศูนย์การแพทย์จุฬา", "คลินิกหมอสมชาย", "  โรงพยาบาลกรุงเทพ  "],
)
def test_known_prefix_is_kept(name):
    assert hospital(name) == " ".join(name.split())


def test_bare_name_gets_hospital_prefix():
    assert hospital("กรุงเทพ") == "โรงพยาบาลกรุงเทพ"


def test_never_doubles_the_word():
    for name in ["โรงพยาบาลสมิติเวช", "สมิติเวช"]:
        assert "โรงพยาบาลโรงพยาบาล" not in hospital(name)
        assert "โรงพยาบาล โรงพยาบาล" not in hospital(name)


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        hospital("  ")
