import pytest
from backend.app.pipeline.sentence_chunker import chunk_sentences

@pytest.mark.asyncio
async def test_chunk_sentences_english():
    async def token_gen():
        for t in ["Hello", " world.", " How", " are", " you", " today?"]:
            yield t

    chunks = []
    async for c in chunk_sentences(token_gen()):
        chunks.append(c)

    assert len(chunks) == 2
    assert chunks[0] == "Hello world."
    assert chunks[1] == "How are you today?"

@pytest.mark.asyncio
async def test_chunk_sentences_hindi_purna_viram():
    async def token_gen():
        for t in ["यह एक परीक्षण है।", " अगला वाक्य यहाँ है।"]:
            yield t

    chunks = []
    async for c in chunk_sentences(token_gen()):
        chunks.append(c)

    assert len(chunks) == 2
    assert "परीक्षण है।" in chunks[0]
    assert "यहाँ है।" in chunks[1]
