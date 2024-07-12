from __future__ import annotations

import re
import inspect

from bisect import bisect_left
from typing import Callable, Sequence, TYPE_CHECKING
from functools import cache
from itertools import accumulate
from contextlib import suppress

import mpire

from tqdm import tqdm

if TYPE_CHECKING: import tiktoken, tokenizers, transformers


_memoized_token_counters = {}
"""A map of token counters to their memoized versions."""

_NON_WHITESPACE_SEMANTIC_SPLITTERS = (
    '.', '?', '!', '*', # Sentence terminators.
    ';', ',', '(', ')', '[', ']', "“", "”", '‘', '’', "'", '"', '`', # Clause separators.
    ':', '—', '…', # Sentence interrupters.
    '/', '\\', '–', '&', '-', # Word joiners.
)
"""A tuple of semantically meaningful non-whitespace splitters that may be used to chunk texts, ordered from most desirable to least desirable."""


def _split_text(text: str) -> tuple[str, bool, list[str]]:
    """Split text using the most semantically meaningful splitter possible."""
    
    splitter_is_whitespace = True

    # Try splitting at, in order of most desirable to least desirable:
    # - The largest sequence of newlines and/or carriage returns;
    # - The largest sequence of tabs;
    # - The largest sequence of whitespace characters; and
    # - A semantically meaningful non-whitespace splitter.
    if '\n' in text or '\r' in text:
        splitter = max(re.findall(r'[\r\n]+', text))
    
    elif '\t' in text:
        splitter = max(re.findall(r'\t+', text))
    
    elif re.search(r'\s', text):
        splitter = max(re.findall(r'\s+', text))
    
    else:
        # Identify the most desirable semantically meaningful non-whitespace splitter present in the text.
        for splitter in _NON_WHITESPACE_SEMANTIC_SPLITTERS:
            if splitter in text:
                splitter_is_whitespace = False
                break
        
        # If no semantically meaningful splitter is present in the text, return an empty string as the splitter and the text as a list of characters.
        else: # NOTE This code block will only be executed if the for loop completes without breaking.
            return '', splitter_is_whitespace, list(text)
    
    # Return the splitter and the split text.
    return splitter, splitter_is_whitespace, text.split(splitter)

def merge_splits(splits: list[str], chunk_size: int, splitter: str, token_counter: Callable) -> tuple[int, str]:
    """Merge splits until a chunk size is reached, returning the index of the last split included in the merged chunk along with the merged chunk itself."""
    
    average = 0.2
    low = 0
    high = len(splits) + 1
    cumulative_lengths = list(accumulate([len(split) for split in splits], initial=0))
    cumulative_lengths.append(cumulative_lengths[-1])

    while low < high:
        i = bisect_left(cumulative_lengths[low : high + 1], chunk_size * average)
        midpoint = min(i + low, high - 1)

        tokens = token_counter(splitter.join(splits[:midpoint]))

        average = cumulative_lengths[midpoint] / tokens if cumulative_lengths[midpoint] and tokens > 0 else average

        if tokens > chunk_size:
            high = midpoint
        else:
            low = midpoint + 1

    return low - 1, splitter.join(splits[:low - 1])

def chunk(
    text: str,
    chunk_size: int,
    token_counter: Callable[[str], int],
    memoize: bool = True,
    _recursion_depth: int = 0,
    _reattach_whitespace_splitters: bool = False,
) -> list[str]:
    """Split a text into semantically meaningful chunks of a specified size as determined by the provided token counter.

    Args:
        text (str): The text to be chunked.
        chunk_size (int): The maximum number of tokens a chunk may contain.
        token_counter (Callable[[str], int]): A callable that takes a string and returns the number of tokens in it.
        memoize (bool, optional): Whether to memoize the token counter. Defaults to `True`.
    
    Returns:
        list[str]: A list of chunks up to `chunk_size`-tokens-long, with any whitespace used to split the text removed."""
    
    # If this is not a recursive call and memoization is enabled, overwrite the `token_counter` with a memoized version of itself.
    if not _recursion_depth and memoize:
        token_counter = _memoized_token_counters.setdefault(token_counter, cache(token_counter))

    # Split the text using the most semantically meaningful splitter possible.
    splitter, splitter_is_whitespace, splits = _split_text(text)
    if _reattach_whitespace_splitters: splitter_is_whitespace = False
    
    chunks = []
    skips = set()
    """A list of indices of splits to skip because they have already been added to a chunk."""
    
    # Iterate through the splits.
    for i, split in enumerate(splits):
        # Skip the split if it has already been added to a chunk.
        if i in skips:
            continue
        
        # If the split is over the chunk size, recursively chunk it.
        if token_counter(split) > chunk_size:
            chunks.extend(chunk(split, chunk_size, token_counter = token_counter, memoize = memoize, _recursion_depth = _recursion_depth + 1, _reattach_whitespace_splitters = _reattach_whitespace_splitters))

        # If the split is equal to or under the chunk size, add it and any subsequent splits to a new chunk until the chunk size is reached.
        else:
            # Merge the split with subsequent splits until the chunk size is reached.
            final_split_in_chunk_i, new_chunk = merge_splits(splits[i:], chunk_size, splitter, token_counter)
            
            # Mark any splits included in the new chunk for exclusion from future chunks.
            skips.update(range(i + 1, i + final_split_in_chunk_i))
            
            # Add the chunk.
            chunks.append(new_chunk)

        # If the splitter is not whitespace and the split is not the last split, add the splitter to the end of the last chunk if doing so would not cause it to exceed the chunk size otherwise add the splitter as a new chunk.
        if not splitter_is_whitespace and not (i == len(splits) - 1 or all(j in skips for j in range(i + 1, len(splits)))):
            if token_counter(last_chunk_with_splitter := chunks[-1] + splitter) <= chunk_size:
                chunks[-1] = last_chunk_with_splitter
            else:
                chunks.append(splitter)
    
    # If this is not a recursive call, remove any empty chunks.
    if not _recursion_depth:
        chunks = list(filter(None, chunks))
    
    return chunks


class Chunker:    
    def __init__(self, chunk_size: int, token_counter: Callable[[str], int]) -> None:
        self.chunk_size = chunk_size
        self.token_counter = token_counter
    
    def chunk(self, text: str) -> list[str]:
        """Chunk a text."""
        
        return chunk(text, self.chunk_size, self.token_counter, memoize = False)
    
    def __call__(
        self,
        text_or_texts: str | Sequence[str],
        processes: int = 1,
        progress: bool = False,
    ) -> list[str] | list[list[str]]:
        """Split text or texts into semantically meaningful chunks of a specified size as determined by the provided tokenizer or token counter.
        
        Args:
            text_or_texts (str | Sequence[str]): The text or texts to be chunked.
        
        Returns:
            list[str] | list[list[str]]: If a single text has been provided, a list of chunks up to `chunk_size`-tokens-long, with any whitespace used to split the text removed, or, if multiple texts have been provided, a list of lists of chunks, with each inner list corresponding to the chunks of one of the provided input texts.
            processes (int, optional): The number of processes to use when chunking multiple texts. Defaults to `1` in which case chunking will occur in the main process.
            progress (bool, optional): Whether to display a progress bar when chunking multiple texts. Defaults to `False`."""
        if isinstance(text_or_texts, str):
            return self.chunk(text_or_texts)
        
        if progress and processes == 1:
            text_or_texts = tqdm(text_or_texts)
        
        if processes == 1:
            return [self.chunk(text) for text in text_or_texts]
        
        with mpire.WorkerPool(processes, use_dill = True) as pool:
            return pool.map(self.chunk, text_or_texts, progress_bar = progress)

def chunkerify(
    tokenizer_or_token_counter: str | tiktoken.Encoding | transformers.PreTrainedTokenizer \
                                | tokenizers.Tokenizer | Callable[[str], int],
    chunk_size: int | None = None,
    max_token_chars: int | None = None,
    memoize: bool = True,
) -> Chunker:
    """Construct a chunker that splits one or more texts into semantically meaningful chunks of a specified size as determined by the provided tokenizer or token counter.
    
    Args:
        tokenizer_or_token_counter (str | tiktoken.Encoding | transformers.PreTrainedTokenizer | tokenizers.Tokenizer | Callable[[str], int]): Either: the name of a `tiktoken` or `transformers` tokenizer (with priority given to the former); a tokenizer that possesses an `encode` attribute (eg, a `tiktoken`, `transformers` or `tokenizers` tokenizer); or a token counter that returns the number of tokens in a input.
        chunk_size (int, optional): The maximum number of tokens a chunk may contain. Defaults to `None` in which case it will be set to the same value as the tokenizer's `model_max_length` attribute (deducted by the number of tokens returned by attempting to tokenize an empty string) if possible otherwise a `ValueError` will be raised.
        max_token_chars (int, optional): The maximum numbers of characters a token may contain. Used to significantly speed up the token counting of long inputs. Defaults to `None` in which case it will either not be used or will, if possible, be set to the numbers of characters in the longest token in the tokenizer's vocabulary as determined by the `token_byte_values` or `get_vocab` methods.
        memoize (bool, optional): Whether to memoize the token counter. Defaults to `True`.
    
    Returns:
        Callable[[str | Sequence[str], bool, bool], list[str] | list[list[str]]]: A chunker that takes either a single text or a sequence of texts and returns, if a single text has been provided, a list of chunks up to `chunk_size`-tokens-long with any whitespace used to split the text removed, or, if multiple texts have been provided, a list of lists of chunks, with each inner list corresponding to the chunks of one of the provided input texts.
        
        The resulting chunker can be passed a `processes` argument that specifies the number of processes to be used when chunking multiple texts.
        
        It is also possible to pass a `progress` argument which, if set to `True` and multiple texts are passed, will display a progress bar.
        
        Technically, the chunker will be an instance of the `semchunk.Chunker` class to assist with type hinting, though this should have no impact on how it can be used."""
    
    # If the provided tokenizer is a string, try to load it with either `tiktoken` or `transformers` or raise an error if neither is available.
    if isinstance(tokenizer_or_token_counter, str):
        try:
            import tiktoken
            
            try:
                tokenizer = tiktoken.encoding_for_model(tokenizer_or_token_counter)
            
            except Exception:
                tokenizer = tiktoken.get_encoding(tokenizer_or_token_counter)
        
        except Exception:
            try:
                import transformers
                
                tokenizer = transformers.AutoTokenizer.from_pretrained(tokenizer_or_token_counter)
            
            except Exception:
                raise ValueError(f'"{tokenizer_or_token_counter}" was provided to `semchunk.chunkerify` as the name of a tokenizer but neither `tiktoken` nor `transformers` have a tokenizer by that name. Perhaps they are not installed or maybe there is a typo in that name?')
        
        tokenizer_or_token_counter = tokenizer
    
    # If the number of characters in the longest token has not been provided, determine it if possible.
    if max_token_chars is None:
        for potential_vocabulary_getter_function in (
            'token_byte_values', # Employed by `tiktoken`.
            'get_vocab', # Employed by `tokenizers`.
        ):
            if hasattr(tokenizer_or_token_counter, potential_vocabulary_getter_function) and callable(getattr(tokenizer_or_token_counter, potential_vocabulary_getter_function)):
                vocab = getattr(tokenizer_or_token_counter, potential_vocabulary_getter_function)()
                
                if hasattr(vocab, '__iter__') and vocab and all(hasattr(token, '__len__') for token in vocab):
                    max_token_chars = max(len(token) for token in vocab)
                    break
    
    # If a chunk size has not been specified, set it to the maximum number of tokens the tokenizer supports if possible otherwise raise an error.
    if chunk_size is None:
        if hasattr(tokenizer_or_token_counter, 'model_max_length') and isinstance(tokenizer_or_token_counter.model_max_length, int):
            chunk_size = tokenizer_or_token_counter.model_max_length
            
            # Attempt to reduce the chunk size by the number of special characters typically added by the tokenizer.
            if hasattr(tokenizer_or_token_counter, 'encode'):
                with suppress(Exception):
                    chunk_size -= len(tokenizer_or_token_counter.encode(''))
        
        else:
            raise ValueError("Your desired chunk size was not passed to `semchunk.chunkerify` and the provided tokenizer either lacks an attribute named 'model_max_length' or that attribute is not an integer. Either specify a chunk size or provide a tokenizer that has a 'model_max_length' attribute that is an integer.")
    
    # If we have been given a tokenizer, construct a token counter from it.
    if hasattr(tokenizer_or_token_counter, 'encode'):
        # Determine whether the tokenizer accepts the argument `add_special_tokens` and, if so, ensure that it is always disabled.
        if 'add_special_tokens' in inspect.signature(tokenizer_or_token_counter.encode).parameters:
            def token_counter(text: str) -> int:
                return len(tokenizer_or_token_counter.encode(text, add_special_tokens = False))
        
        else:
            def token_counter(text: str) -> int:
                return len(tokenizer_or_token_counter.encode(text))
    
    else:
        token_counter = tokenizer_or_token_counter
    
    # If we know the number of characters in the longest token, construct a new token counter that uses that to avoid having to tokenize very long texts.
    if max_token_chars is not None:
        max_token_chars = max_token_chars - 1
        original_token_counter = token_counter
        
        def faster_token_counter(text: str) -> int:
            heuristic = chunk_size * 6
            
            if len(text) > heuristic and original_token_counter(text[:heuristic + max_token_chars]) > chunk_size:
                return chunk_size + 1
            
            return original_token_counter(text)

        token_counter = faster_token_counter
    
    # Memoize the token counter if necessary.
    if memoize:
        token_counter = _memoized_token_counters.setdefault(token_counter, cache(token_counter))
    
    # Construct and return the chunker.
    return Chunker(chunk_size, token_counter)