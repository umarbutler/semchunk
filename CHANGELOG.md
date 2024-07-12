## Changelog 🔄
All notable changes to `semchunk` will be documented here. This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2024-07-12
### Changed
- Switched from having `chunkerify()` output a function to having it return an instance of the new `Chunker()` class which should not alter functionality in any way but will allow for the preservation of type hints, fixing [#7](https://github.com/umarbutler/semchunk/pull/7).

## [2.1.0] - 2024-06-20
### Fixed
- Ceased memoizing `chunk()` (but not token counters) due to the fact that cached outputs of memoized functions are shallow rather than deep copies of original outputs, meaning that if one were to chunk a text and then chunk that same text again and then modify one of the chunks outputted by the first call, the chunks outputted by the second call would also be modified. This behaviour is not expected and therefore undesirable. The memoization of token counters is not impacted as they output immutable objects, namely, integers.

## [2.0.0] - 2024-06-19
### Added
- Added support for multiprocessing through the `processes` argument passable to chunkers constructed by `chunkerify()`.

### Removed
- No longer guaranteed that `semchunk` is pure Python.

## [1.0.1] - 2024-06-02
### Fixed
- Documented the `progress` argument in the docstring for `chunkerify()` and its type hint in the README.

## [1.0.0] - 2024-06-02
### Added
- Added a `progress` argument to the chunker returned by `chunkerify()` that, when set to `True` and multiple texts are passed, displays a progress bar.

## [0.3.2] - 2024-06-01
### Fixed
- Fixed a bug where a `DivisionByZeroError` would be raised where a token counter returned zero tokens when called from `merge_splits()`, courtesy of [@jcobol](https://github.com/jcobol) ([#5](https://github.com/umarbutler/semchunk/pull/5)) ([7fd64eb](https://github.com/umarbutler/semchunk/pull/5/commits/7fd64eb8cf51f45702c59f43795be9a00c7d0d17)), fixing [#4](https://github.com/umarbutler/semchunk/issues/4).

## [0.3.1] - 2024-05-18
### Fixed
- Fixed typo in error messages in `chunkerify()` where it was referred to as `make_chunker()`.

## [0.3.0] - 2024-05-18
### Added
- Introduced the `chunkerify()` function, which constructs a chunker from a tokenizer or token counter that can be reused and can also chunk multiple texts in a single call. The resulting chunker speeds up chunking by 40.4% thanks, in large part, to a token counter that avoid having to count the number of tokens in a text when the number of characters in the text exceed a certain threshold, courtesy of [@R0bk](https://github.com/R0bk) ([#3](https://github.com/umarbutler/semchunk/pull/3)) ([337a186](https://github.com/umarbutler/semchunk/pull/3/commits/337a18615f991076b076262288b0408cb162b48c)).

## [0.2.4] - 2024-05-13
### Changed
- Improved chunking performance with larger chunk sizes by switching from linear to binary search for the identification of optimal chunk boundaries, courtesy of [@R0bk](https://github.com/R0bk) ([#3](https://github.com/umarbutler/semchunk/pull/3)) ([337a186](https://github.com/umarbutler/semchunk/pull/3/commits/337a18615f991076b076262288b0408cb162b48c)).

## [0.2.3] - 2024-03-11
### Fixed
- Ensured that memoization does not overwrite `chunk()`'s function signature.

## [0.2.2] - 2024-02-05
### Fixed
- Ensured that the `memoize` argument is passed back to `chunk()` in recursive calls.

## [0.2.1] - 2023-11-09
### Added
- Memoized `chunk()`.

### Fixed
- Fixed typos in README.

## [0.2.0] - 2023-11-07
### Added
- Added the `memoize` argument to `chunk()`, which memoizes token counters by default to significantly improve performance.

### Changed
- Improved chunking performance.

## [0.1.2] - 2023-11-07
### Fixed
- Fixed links in the README.

## [0.1.1] - 2023-11-07
### Added
- Added new test samples.
- Added benchmarks.

### Changed
- Improved chunking performance.
- improved test coverage.

## [0.1.0] - 2023-11-05
### Added
- Added the `chunk()` function, which splits text into semantically meaningful chunks of a specified size as determined by a provided token counter.

[2.2.0]: https://github.com/umarbutler/semchunk/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/umarbutler/semchunk/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/umarbutler/semchunk/compare/v1.0.1...v2.0.0
[1.0.1]: https://github.com/umarbutler/semchunk/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/umarbutler/semchunk/compare/v0.3.2...v1.0.0
[0.3.2]: https://github.com/umarbutler/semchunk/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/umarbutler/semchunk/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/umarbutler/semchunk/compare/v0.2.4...v0.3.0
[0.2.4]: https://github.com/umarbutler/semchunk/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/umarbutler/semchunk/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/umarbutler/semchunk/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/umarbutler/semchunk/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/umarbutler/semchunk/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/umarbutler/semchunk/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/umarbutler/semchunk/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/umarbutler/semchunk/releases/tag/v0.1.0