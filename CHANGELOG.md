## Changelog 🔄
All notable changes to `semchunk` will be documented here. This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Memoized `chunk()`.

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

[0.2.0]: https://github.com/umarbutler/semchunk/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/umarbutler/semchunk/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/umarbutler/semchunk/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/umarbutler/semchunk/releases/tag/v0.1.0