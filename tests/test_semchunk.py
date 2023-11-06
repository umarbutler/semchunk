"""Test semchunk."""
import semchunk
import tiktoken
import nltk

# Download the Gutenberg corpus.
nltk.download('gutenberg')
gutenberg = nltk.corpus.gutenberg

# Initalise the encoder.
encoder = tiktoken.encoding_for_model('gpt-4')

def _token_counter(text: str) -> int:
    """Count the number of tokens in a text."""
    
    return len(encoder.encode(text))

def test_chunk() -> None:
    """Test `semchunk.chunk()`."""
    
    # Test a variety of chunk sizes.
    for chunk_size in {1, 2, 512}:
        # Test a variety of texts.
        for fileid in {'austen-emma.txt', 'carroll-alice.txt', 'shakespeare-macbeth.txt'}:
            sample = gutenberg.raw(fileid)
            for chunk in semchunk.chunk(sample, chunk_size=chunk_size, token_counter=_token_counter):
                assert _token_counter(chunk) <= chunk_size
            
            # Test that recombining lowercased chunks stripped of whitespace yields the original text.
            lowercased_no_whitespace = ''.join(sample.lower().split())
            assert ''.join(semchunk.chunk(lowercased_no_whitespace, chunk_size, _token_counter)) == lowercased_no_whitespace
    
    # Test a string where tabs must be used as splitters (to increase code coverage).
    assert semchunk.chunk('ThisIs\tATest.', 4, _token_counter) == ['ThisIs', 'ATest.']