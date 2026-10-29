import pytest
from backend.app.pipeline.codeswitch import (
    split_by_script,
    tag_languages,
    matrix_language,
    is_code_switched
)

def test_split_by_script_english():
    text = "Hello world"
    spans = split_by_script(text)
    assert len(spans) == 1
    assert spans[0].script == "LATIN"

def test_split_by_script_hindi():
    text = "नमस्ते दुनिया"
    spans = split_by_script(text)
    assert len(spans) == 1
    assert spans[0].script == "DEVANAGARI"

def test_split_by_script_mixed():
    text = "Hello नमस्ते world"
    spans = split_by_script(text)
    assert len(spans) == 3
    assert spans[0].script == "LATIN"
    assert spans[1].script == "DEVANAGARI"
    assert spans[2].script == "LATIN"

def test_tag_languages_hinglish():
    text = "Aaj ka kya scene hai bhai?"
    spans = split_by_script(text)
    tagged = tag_languages(spans)
    assert tagged[0].lang == "hi"

def test_matrix_language():
    text = "Main kal subah Delhi ja raha hoon for an urgent meeting."
    spans = split_by_script(text)
    tagged = tag_languages(spans)
    mat = matrix_language(tagged)
    assert mat == "hi"
