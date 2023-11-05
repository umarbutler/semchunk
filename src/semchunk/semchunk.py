import re

NON_WHITESPACE_SEMANTIC_SPLITTERS = (
    '.', '?', '!', '*', # Sentence terminators.
    ';', ',', '(', ')', '[', ']', "“", "”", '‘', '’', "'", '"', '`', # Clause separators.
    ':', '—', '…', # Sentence interrupters.
    '/', '\\', '–', '&', '-', # Word joiners.
)
"""A tuple of semantically meaningful non-whitespace splitters that may be used to chunk texts, ordered from most desirable to least desirable."""
    
def _split_text(text: str) -> tuple[str, list[str]]:
    """Split text using the most semantically meaningful splitter possible."""

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
        for splitter in NON_WHITESPACE_SEMANTIC_SPLITTERS:
            if splitter in text:
                break
        
        # If no semantically meaningful splitter is present in the text, return an empty string as the splitter and the text as a list of characters.
        else: # NOTE This code block will only be executed if the for loop completes without breaking.
            return '', list(text)
    
    # Return the splitter and the split text.
    return splitter, text.split(splitter)

def chunk(text: str, chunk_size: int, token_counter: callable, _recursion_depth: int = 0) -> list[str]:
    """Split text into semantically meaningful chunks of a specified size as determined by the provided token counter.

   Args:
        text (str): The text to be chunked.
        chunk_size (int): The maximum number of tokens a chunk may contain.
        token_counter (callable): A callable that takes a string and returns the number of tokens in it.
    
    Returns:
        list[str]: A list of chunks up to `chunk_size`-tokens-long, with any whitespace used to split the text removed."""
    
    # If the text is already within the chunk size, return it as the only chunk.
    if token_counter(text) <= chunk_size:
        return [text]

    # Split the text using the most semantically meaningful splitter possible.
    splitter, splits = _split_text(text)
    
    # Flag whether the splitter is whitespace.
    splitter_is_whitespace = not splitter.split()
    
    chunks = []
    skips = []
    """A list of indices of splits to skip because they have already been added to a chunk."""
    
    # Iterate through the splits.
    for i, split in enumerate(splits):
        # Skip the split if it has already been added to a chunk.
        if i in skips:
            continue
        
        # If the split is over the chunk size, recursively chunk it.
        if token_counter(split) > chunk_size:
            chunks.extend(chunk(split, chunk_size, token_counter=token_counter, _recursion_depth=_recursion_depth+1))

        # If the split is equal to or under the chunk size, merge it with all subsequent splits until the chunk size is reached.
        else:
            # Initialise a list of splits to be merged into a new chunk.
            new_chunk = [split]
            
            # Iterate through each subsequent split until the chunk size is reached.
            for j, next_split in enumerate(splits[i+1:], start=i+1):
                # Check whether the next split can be added to the chunk without exceeding the chunk size.
                if token_counter(splitter.join(new_chunk+[next_split])) <= chunk_size:
                    # Add the next split to the chunk.
                    new_chunk.append(next_split)
                    
                    # Add the index of the next split to the list of indices to skip.
                    skips.append(j)
                
                # If the next split cannot be added to the chunk without exceeding the chunk size, break.
                else:
                    break
            
            # Join the splits with the splitter.
            new_chunk = splitter.join(new_chunk)
            
            # Add the chunk.
            chunks.append(new_chunk)

        # If the splitter is not whitespace and the split is not the last split, add the splitter to the end of the last chunk if doing so would not cause it to exceed the chunk size otherwise add the splitter as a new chunk.
        if not splitter_is_whitespace and not (i == len(splits) - 1 or all(j in skips for j in range(i+1, len(splits)))):
            if token_counter(chunks[-1]+splitter) <= chunk_size:
                chunks[-1] += splitter
            
            else:
                chunks.append(splitter)
    
    # If this is not a recursive call, remove any empty chunks.
    if not _recursion_depth:
        chunks = [chunk for chunk in chunks if chunk]
    
    return chunks