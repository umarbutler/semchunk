import time

import semchunk

import nltk
import tiktoken

from semantic_text_splitter import TextSplitter

# BEGIN CONFIG #
CHUNK_SIZE = 512
# END CONFIG #

def bench() -> dict[str, float]:
    # Initialise the chunkers.
    semchunk_chunker = semchunk.chunkerify(tiktoken.encoding_for_model('gpt-4'), CHUNK_SIZE)
    semantic_text_splitter_chunker = TextSplitter.from_tiktoken_model('gpt-4', CHUNK_SIZE)

    def bench_semchunk(text: str) -> None:
        semchunk_chunker(text)

    def bench_semantic_text_splitter(text: str) -> None:
        semantic_text_splitter_chunker.chunks(text)

    libraries = {
        'semchunk': bench_semchunk,
        #'semantic_text_splitter': bench_semantic_text_splitter,
    }

    # Download the Gutenberg corpus.
    nltk.download('gutenberg')
    gutenberg = nltk.corpus.gutenberg
    
    # Benchmark the libraries.
    benchmarks = dict.fromkeys(libraries.keys(), 0)
    
    for fileid in gutenberg.fileids():
        sample = gutenberg.raw(fileid)
        for library, function in libraries.items():
            start = time.time()
            function(sample)
            benchmarks[library] += time.time() - start
    
    return benchmarks

if __name__ == '__main__':
    for library, time_taken in bench().items():
        print(f'{library}: {time_taken:.2f}s')