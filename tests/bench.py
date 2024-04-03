import time

import test_semchunk
import tiktoken
from semantic_text_splitter import TextSplitter

import semchunk

chunk_sizes = [8,16,32,64,128,256,512,1024]
semantic_text_splitter_chunker = TextSplitter.from_tiktoken_model('gpt-4')

encoder = tiktoken.encoding_for_model('gpt-4')

def _token_counterv1(text: str) -> int:
    """Count the number of tokens in a text."""
    return len(encoder.encode(text))

def _token_counterv2(text: str) -> int:
    """Count the number of tokens in a text."""
    return len(encoder.encode(text))

def bench_semchunkv1(text: str, chunk_size: int) -> list[str]:
    return semchunk.chunk_legacy(text, chunk_size=chunk_size, token_counter=_token_counterv1)

def bench_semchunkv2(text: str, chunk_size: int) -> list[str]:
    return semchunk.chunk(text, chunk_size=chunk_size, token_counter=_token_counterv2)

def bench_semantic_text_splitter(text: str, chunk_size: int) -> None:
    semantic_text_splitter_chunker.chunks(text, chunk_size)

libraries = {
    'semchunk': bench_semchunkv1,
    'semchunkv2': bench_semchunkv2,
    'semantic_text_splitter': bench_semantic_text_splitter,
}

def bench() -> dict[str, float]:
    benchmarks = {k: [0]*len(chunk_sizes) for k in libraries.keys()}
    
    for i, chunk_size in enumerate(chunk_sizes):
        semchunk.semchunk._memoised_token_counters = {}
        for fileid in test_semchunk.gutenberg.fileids():
            sample = test_semchunk.gutenberg.raw(fileid)
            for library, function in libraries.items():
                start = time.time()
                function(sample, chunk_size)
                benchmarks[library][i] += time.time() - start
        
    return benchmarks

if __name__ == '__main__':
    print('\t\t' + '\t'.join(map(str, chunk_sizes)))
    for library, times_taken in bench().items():
        times = '\t'.join(f'{time:.2f}s' for time in times_taken)
        print(f'{library}:\t {times}')