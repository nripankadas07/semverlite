# semverlite

Strict semantic versioning 2.0.0 parsing, comparison, and utilities for Python developers.

## Installation

```bash
pip install semverlite
```

## Quick Start

```python
from semverlite import Version

# Parse a version string
v = Version.parse("1.2.3")
print(v.major, v.minor, v.patch)  # 1 2 3

# Parse with prerelease and build metadata
v = Version.parse("1.2.3-alpha.1+build.456")
print(v.prerelease)       # ("alpha", 1)
print(v.build_metadata)   # ("build", 456)

# Compare versions
v1 = Version.parse("1.0.0-alpha")
v2 = Version.parse("1.0.0")
print(v1 < v2)  # True (prerelease < release)

# Check if stable
print(v2.is_stable)  # True

# Bump versions
v3 = Version.parse("1.2.3")
print(v3.bump_major())  # Version('2.0.0')
print(v3.bump_minor())  # Version('1.3.0')
print(v3.bump_patch())  # Version('1.2.4')
```

## API Reference

### Version Class

#### Class Methods

- **`Version.parse(version_string: str) -> Version`**
  - Parses a semantic version string per semver 2.0.0 specification.
  - Accepts: `"1.2.3"`, `"1.2.3-alpha"`, `"1.2.3+build.123"`, `"1.2.3-alpha.1+build.456"`.
  - Returns a Version instance or raises `SemverError` if invalid.

#### Properties

- **`major: int`** â Major version number (0+).
- **`minor: int`** â Minor version number (0+).
- **`patch: int`** â Patch version number (0+).
- **`prerelease: Optional[Tuple[Union[int, str], ...]]`** â Prerelease identifiers (None if not present).
- **`build_metadata: Optional[Tuple[Union[int, str], ...]]`** â Build metadata identifiers (None if not present).
- **`is_stable: bool`** â True if the version has no prerelease (is a release version).

#### Instance Methods

- **`bump_major() -> Version`**
  - Returns a new Version with major incremented, minor and patch reset to 0.
  - Removes any prerelease or build metadata.

- **`bump_minor() -> Version`**
  - Returns a new Version with minor incremented, patch reset to 0.
  - Removes any prerelease or build metadata.

- **`bump_patch() -> Version`**
  - Returns a new Version with patch incremented.
  - Removes any prerelease or build metadata.

#### Comparison Operators

Versions support full comparison per semver 2.0.0 precedence rules:

- **`==`** â Equal if major, minor, patch, and prerelease match (build metadata ignored).
- **`!=`** â Not equal.
- **`<`** â Less than (prerelease < release, numeric < alphanumeric in prerelease).
- **`<=`** â Less than or equal.
- **`>`** â Greater than.
- **`>=`** â Greater than or equal.

#### String Representation

- **`str(version)`** â Returns the canonical version string (e.g., `"1.2.3-alpha.1+build.456"`).

### SemverError Exception

Raised when parsing fails:

```python
from semverlite import SemverError

try:
    Version.parse("invalid")
except SemverError as e:
    print(f"Invalid version: {e}")
```

## Spec Compliance

`semverlite` strictly adheres to [Semantic Versioning 2.0.0](https://semver.org/):

- **Major.Minor.Patch** â Required; must be non-negative integers without leading zeros.
- **Prerelease** â Optional; dot-separated identifiers of alphanumerics and hyphens. Numeric identifiers compared as integers, alphanumeric as strings. Fewer identifiers sort lower.
- **Build Metadata** â Optional; similar format but ignored in version precedence.
- **Precedence** â Prerelease versions sort lower than release versions. Numeric identifiers in prerelease sort lower than alphanumeric.

## Edge Cases Handled

- Leading zeros in major/minor/patch are invalid (raises `SemverError`).
- Leading zeros in numeric prerelease identifiers are invalid.
- Empty identifiers (e.g., `1.2.3-alpha..1`) are invalid.
- Non-string input raises `SemverError`.
- Missing components (e.g., `"1.2"`) are invalid.
- Extra components (e.g., `"1.2.3.4"`) are invalid.
- Build metadata is ignored in equality and ordering comparisons.

## Running Tests

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=src/semverlite --cov-report=term-missing
```

## License

MIT License. See [LICENSE](LICENSE) file for details.
