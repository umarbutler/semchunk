# semchunk
<a href="https://pypi.org/project/semchunk/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/semchunk"></a> <a href="https://github.com/umarbutler/semchunk/actions/workflows/ci.yml" alt="Build Status"><img src="https://img.shields.io/github/actions/workflow/status/umarbutler/semchunk/ci.yml?branch=main"></a> <a href="https://app.codecov.io/gh/umarbutler/semchunk" alt="Code Coverage"><img src="https://img.shields.io/codecov/c/github/umarbutler/semchunk"></a> <a href="https://pypistats.org/packages/semchunk" alt="Downloads"><img src="https://img.shields.io/pypi/dm/semchunk"></a>

`semchunk` is a fast and lightweight Python library for splitting text into semantically meaningful chunks.

Owing to its complex yet highly efficient chunking algorithm, `semchunk` is both more semantically accurate than [`langchain.text_splitter.RecursiveCharacterTextSplitter`](https://python.langchain.com/v0.2/docs/how_to/recursive_text_splitter/#splitting-text-from-languages-without-word-boundaries) (see [How It Works 🔍](https://github.com/umarbutler/semchunk#how-it-works-)) and is also over 90% faster than [`semantic-text-splitter`](https://pypi.org/project/semantic-text-splitter/) (see the [Benchmarks 📊](https://github.com/umarbutler/semchunk#benchmarks-)).

## Installation 📦
`semchunk` may be installed with `pip`:
```bash
pip install semchunk
```

## Usage 👩‍💻
The code snippet below demonstrates how text can be chunked with `semchunk`:
```python
import semchunk
from transformers import AutoTokenizer # Neither `transformers` nor `tiktoken` are required,
import tiktoken                        # they are here for demonstration purposes.

chunk_size = 2 # A low chunk size is used here for demonstration purposes. Keep in mind that
               # `semchunk` doesn't take special tokens into account unless you're using a
               # custom token counter, so you probably want to deduct your chunk size by the
               # number of special tokens added by your tokenizer.
text = 'The quick brown fox jumps over the lazy dog.'

# As you can see below, `semchunk.chunkerify` will accept the names of all OpenAI models, OpenAI
# `tiktoken` encodings and Hugging Face models (in that order of precedence), along with custom
# tokenizers that have an `encode()` method (such as `tiktoken`, `transformers` and `tokenizers`
# tokenizers) and finally any function that can take a text and return the number of tokens in it.
chunker = semchunk.chunkerify('umarbutler/emubert', chunk_size) or \
          semchunk.chunkerify('gpt-4', chunk_size) or \
          semchunk.chunkerify('cl100k_base', chunk_size) or \
          semchunk.chunkerify(AutoTokenizer.from_pretrained('umarbutler/emubert'), chunk_size) or \
          semchunk.chunkerify(tiktoken.encoding_for_model('gpt-4'), chunk_size) or \
          semchunk.chunkerify(lambda text: len(text.split()), chunk_size)

# The resulting `chunker` can take and chunk a single text or a list of texts, returning a list of
# chunks or a list of lists of chunks, respectively.
assert chunker(text) == ['The quick', 'brown', 'fox', 'jumps', 'over the', 'lazy', 'dog.']
assert chunker([text], progress = True) == [['The quick', 'brown', 'fox', 'jumps', 'over the', 'lazy', 'dog.']]

# If you have a large number of texts to chunk and speed is a concern, you can also enable
# multiprocessing by setting `processes` to a number greater than 1.
assert chunker([text], processes = 2) == [['The quick', 'brown', 'fox', 'jumps', 'over the', 'lazy', 'dog.']]
```

### Chunkerify
```python
def chunkerify(
    tokenizer_or_token_counter: str | tiktoken.Encoding | transformers.PreTrainedTokenizer | \
                                tokenizers.Tokenizer | Callable[[str], int],
    chunk_size: int = None,
    max_token_chars: int = None,
    memoize: bool = True,
) -> Callable[[str | Sequence[str], bool, bool], list[str] | list[list[str]]]:
```

`chunkerify()` constructs a chunker that splits one or more texts into semantically meaningful chunks of a specified size as determined by the provided tokenizer or token counter.

`tokenizer_or_token_counter` is either: the name of a `tiktoken` or `transformers` tokenizer (with priority given to the former); a tokenizer that possesses an `encode` attribute (eg, a `tiktoken`, `transformers` or `tokenizers` tokenizer); or a token counter that returns the number of tokens in a input.

`chunk_size` is the maximum number of tokens a chunk may contain. It defaults to `None` in which case it will be set to the same value as the tokenizer's `model_max_length` attribute (deducted by the number of tokens returned by attempting to tokenize an empty string) if possible otherwise a `ValueError` will be raised.

`max_token_chars` is the maximum numbers of characters a token may contain. It is used to significantly speed up the token counting of long inputs. It defaults to `None` in which case it will either not be used or will, if possible, be set to the numbers of characters in the longest token in the tokenizer's vocabulary as determined by the `token_byte_values` or `get_vocab` methods.

`memoize` flags whether to memoize the token counter. It defaults to `True`.

This function returns a chunker that takes either a single text or a sequence of texts and returns, if a single text has been provided, a list of chunks up to `chunk_size`-tokens-long with any whitespace used to split the text removed, or, if multiple texts have been provided, a list of lists of chunks, with each inner list corresponding to the chunks of one of the provided input texts.

The resulting chunker can be passed a `processes` argument that specifies the number of processes to be used when chunking multiple texts.

It is also possible to pass a `progress` argument which, if set to `True` and multiple texts are passed, will display a progress bar.

Technically, the chunker will be an instance of the `semchunk.Chunker` class to assist with type hinting, though this should have no impact on how it can be used.

### Chunk
```python
def chunk(
    text: str,
    chunk_size: int,
    token_counter: Callable,
    memoize: bool = True,
) -> list[str]
```

`chunk()` splits a text into semantically meaningful chunks of a specified size as determined by the provided token counter.

`text` is the text to be chunked.

`chunk_size` is the maximum number of tokens a chunk may contain.

`token_counter` is a callable that takes a string and returns the number of tokens in it.

`memoize` flags whether to memoize the token counter. It defaults to `True`.

This function returns a list of chunks up to `chunk_size`-tokens-long, with any whitespace used to split the text removed.

## How It Works 🔍
`semchunk` works by recursively splitting texts until all resulting chunks are equal to or less than a specified chunk size. In particular, it:
1. Splits text using the most semantically meaningful splitter possible;
1. Recursively splits the resulting chunks until a set of chunks equal to or less than the specified chunk size is produced;
1. Merges any chunks that are under the chunk size back together until the chunk size is reached; and
1. Reattaches any non-whitespace splitters back to the ends of chunks barring the final chunk if doing so does not bring chunks over the chunk size, otherwise adds non-whitespace splitters as their own chunks.

To ensure that chunks are as semantically meaningful as possible, `semchunk` uses the following splitters, in order of precedence:
1. The largest sequence of newlines (`\n`) and/or carriage returns (`\r`);
1. The largest sequence of tabs;
1. The largest sequence of whitespace characters (as defined by regex's `\s` character class);
1. Sentence terminators (`.`, `?`, `!` and `*`);
1. Clause separators (`;`, `,`, `(`, `)`, `[`, `]`, `“`, `”`, `‘`, `’`, `'`, `"` and `` ` ``);
1. Sentence interrupters (`:`, `—` and `…`);
1. Word joiners (`/`, `\`, `–`, `&` and `-`); and
1. All other characters.

## Benchmarks 📊
On a desktop with a Ryzen 3600, 64 GB of RAM, Windows 11 and Python 3.11.9, it takes `semchunk` 6.69 seconds to split every sample in [NLTK's Gutenberg Corpus](https://www.nltk.org/howto/corpus.html#plaintext-corpora) into 512-token-long chunks with GPT-4's tokenizer (for context, the Corpus contains 18 texts and 3,001,260 tokens). By comparison, it takes [`semantic-text-splitter`](https://pypi.org/project/semantic-text-splitter/) 116.48 seconds to chunk the same texts into 512-token-long chunks — a difference of 94.26%.

The code used to benchmark `semchunk` and `semantic-text-splitter` is available [here](https://github.com/umarbutler/semchunk/blob/main/tests/bench.py).

## Licence 📄
This library is licensed under the [MIT License](https://github.com/umarbutler/semchunk/blob/main/LICENCE).