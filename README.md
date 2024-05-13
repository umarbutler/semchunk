# semchunk
<a href="https://pypi.org/project/semchunk/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/semchunk"></a> <a href="https://github.com/umarbutler/semchunk/actions/workflows/ci.yml" alt="Build Status"><img src="https://img.shields.io/github/actions/workflow/status/umarbutler/semchunk/ci.yml?branch=main"></a> <a href="https://app.codecov.io/gh/umarbutler/semchunk" alt="Code Coverage"><img src="https://img.shields.io/codecov/c/github/umarbutler/semchunk"></a> <!-- <a href="https://pypistats.org/packages/semchunk" alt="Downloads"><img src="https://img.shields.io/pypi/dm/semchunk"></a> -->

`semchunk` is a fast and lightweight pure Python library for splitting text into semantically meaningful chunks.

Owing to its complex yet highly efficient chunking algorithm, `semchunk` is both more semantically accurate than [`langchain.text_splitter.RecursiveCharacterTextSplitter`](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/recursive_text_splitter) (see [How It Works 🔍](https://github.com/umarbutler/semchunk#how-it-works-)) and is also over 80% faster than [`semantic-text-splitter`](https://pypi.org/project/semantic-text-splitter/) (see the [Benchmarks 📊](https://github.com/umarbutler/semchunk#benchmarks-)).

## Installation 📦
`semchunk` may be installed with `pip`:
```bash
pip install semchunk
```

## Usage 👩‍💻
The code snippet below demonstrates how text can be chunked with `semchunk`:
```python
>>> import semchunk
>>> import tiktoken # `tiktoken` is not required but is used here to quickly count tokens.
>>> text = 'The quick brown fox jumps over the lazy dog.'
>>> chunk_size = 2 # A low chunk size is used here for demo purposes.
>>> encoder = tiktoken.encoding_for_model('gpt-4')
>>> token_counter = lambda text: len(encoder.encode(text)) # `token_counter` may be swapped out for any function capable of counting tokens.
>>> semchunk.chunk(text, chunk_size=chunk_size, token_counter=token_counter)
['The quick', 'brown fox', 'jumps over', 'the lazy', 'dog.']
```

### Chunk
```python
def chunk(
    text: str,
    chunk_size: int,
    token_counter: callable,
    memoize: bool=True
) -> list[str]
```

`chunk()` splits text into semantically meaningful chunks of a specified size as determined by the provided token counter.

`text` is the text to be chunked.

`chunk_size` is the maximum number of tokens a chunk may contain.

`token_counter` is a callable that takes a string and returns the number of tokens in it.

`memoize` flags whether to memoise the token counter. It defaults to `True`.

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

`semchunk` also relies on memoization to cache the results of token counters and the `chunk()` function, thereby improving performance.

## Benchmarks 📊
On a desktop with a Ryzen 3600, 64 GB of RAM, Windows 11 and Python 3.12.0, it takes `semchunk` 14.11s seconds to split every sample in [NLTK's Gutenberg Corpus](https://www.nltk.org/howto/corpus.html#plaintext-corpora) into 512-token-long chunks with GPT-4's tokenizer (for context, the Corpus contains 18 texts and 3,001,260 tokens). By comparison, it takes [`semantic-text-splitter`](https://pypi.org/project/semantic-text-splitter/) 2 minutes and 56.1 seconds to chunk the same texts into 512-token-long chunks — a difference of 87.84%.

The code used to benchmark `semchunk` and `semantic-text-splitter` is available [here](https://github.com/umarbutler/semchunk/blob/main/tests/bench.py).

## Licence 📄
This library is licensed under the [MIT License](https://github.com/umarbutler/semchunk/blob/main/LICENCE).