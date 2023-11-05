# semchunk
<a href="https://pypi.org/project/semchunk/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/semchunk"></a> <a href="https://github.com/umarbutler/semchunk/actions/workflows/ci.yml" alt="Build Status"><img src="https://img.shields.io/github/actions/workflow/status/umarbutler/semchunk/ci.yml?branch=main"></a> <a href="https://app.codecov.io/gh/umarbutler/semchunk" alt="Code Coverage"><img src="https://img.shields.io/codecov/c/github/umarbutler/semchunk"></a> <!-- <a href="https://pypistats.org/packages/semchunk" alt="Downloads"><img src="https://img.shields.io/pypi/dm/semchunk"></a> -->

`semchunk` is a fast and lightweight pure Python library for splitting text into semantically meaningful chunks.

## Installation 📦
`semchunk` may be installed with `pip`:
```bash
pip install semchunk
```

## Usage 👩‍💻
The code snippet below demonstrates how text can be chunked with `semchunk`:

```python
>>> import semchunk
>>> text = 'The quick brown fox jumps over the lazy dog.'
>>> token_counter = lambda text: len(text.split()) # If using `tiktoken`, you may replace this with `token_counter = lambda text: len(tiktoken.encoding_for_model(model).encode(text))`.
>>> semchunk.chunk(text, chunk_size=2, token_counter=token_counter)
['The quick', 'brown fox', 'jumps over', 'the lazy', 'dog.']
```

### Chunk
```python
def chunk(
    text: str,
    chunk_size: int,
    token_counter: callable,
) -> list[str]
```

`chunk()` splits text into semantically meaningful chunks of a specified size as determined by the provided token counter.

`text` is the text to be chunked.

`chunk_size` is the maximum number of tokens a chunk may contain.

`token_counter` is a callable that takes a string and returns the number of tokens in it.

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

## Licence 📄
This library is licensed under the [MIT License](https://github.com/umarbutler/semchunk/blob/main/LICENSE).