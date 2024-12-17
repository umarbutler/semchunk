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
    sts_chunker = TextSplitter.from_tiktoken_model('gpt-4', CHUNK_SIZE)

    # Initalise the benchmarking functions.
    def bench_semchunk(texts: list[str]) -> None:
        semchunk_chunker(texts)

    def bench_sts(texts: list[str]) -> None:
        sts_chunker.chunk_all(texts)

    libraries = {
        'semchunk': bench_semchunk,
        'semantic_text_splitter': bench_sts,
    }

    # Download the Gutenberg corpus.
    try:
        gutenberg = nltk.corpus.gutenberg

    except Exception:
        nltk.download('gutenberg')
        gutenberg = nltk.corpus.gutenberg

    # Benchmark the libraries.
    benchmarks = dict.fromkeys(libraries.keys(), 0.0)
    texts = [gutenberg.raw(fileid) for fileid in gutenberg.fileids()]

    for library, function in libraries.items():
        start = time.time()
        function(texts)
        benchmarks[library] = time.time() - start

    return benchmarks

if __name__ == '__main__':
    nltk.download('gutenberg')
    
    for library, time_taken in bench().items():
        print(f'{library}: {time_taken:.2f}s')
