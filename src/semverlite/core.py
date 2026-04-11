"""Core semverlite implementation â strict semver 2.0.0 parsing and comparison."""

from typing import Optional, Tuple, Union


class SemverError(Exception):
    """Raised when a version string cannot be parsed per semver 2.0.0 spec."""

    pass


class Version:
    """Immutable semantic version object conforming to semver 2.0.0."""

    __slots__ = ("_major", "_minor", "_patch", "_prerelease", "_build_metadata")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: Optional[Tuple[Union[int, str], ...]] = None,
        build_metadata: Optional[Tuple[Union[int, str], ...]] = None,
    ) -> None:
        """Initialize a Version instance.

        Args:
            major: Major version number (non-negative integer).
            minor: Minor version number (non-negative integer).
            patch: Patch version number (non-negative integer).
            prerelease: Optional tuple of prerelease identifiers.
            build_metadata: Optional tuple of build metadata identifiers.
        """
        self._major = major
        self._minor = minor
        self._patch = patch
        self._prerelease = prerelease
        self._build_metadata = build_metadata

    @property
    def major(self) -> int:
        """Major version number."""
        return self._major

    @property
    def minor(self) -> int:
        """Minor version number."""
        return self._minor

    @property
    def patch(self) -> int:
        """Patch version number."""
        return self._patch

    @property
    def prerelease(self) -> Optional[Tuple[Union[int, str], ...]]:
        """Prerelease identifiers, or None if not present."""
        return self._prerelease

    @property
    def build_metadata(self) -> Optional[Tuple[Union[int, str], ...]]:
        """Build metadata identifiers, or None if not present."""
        return self._build_metadata

    @property
    def is_stable(self) -> bool:
        """True if this is a stable release (no prerelease)."""
        return self._prerelease is None

    @staticmethod
    def parse(version_string: str) -> "Version":
        """Parse a semantic version string.

        Args:
            version_string: A version string like '1.2.3', '1.2.3-alpha', or '1.2.3+build'.

        Returns:
            A Version instance.

        Raises:
            SemverError: If the version string is invalid per semver 2.0.0 spec.
        """
        if not isinstance(version_string, str):
            raise SemverError(
                f"Version must be a string, got {type(version_string).__name__}"
            )

        if not version_string:
            raise SemverError("Version string cannot be empty")

        version_string = version_string.strip()

        # Split off build metadata
        build_metadata: Optional[Tuple[Union[int, str], ...]] = None
        if "+" in version_string:
            version_string, build_part = version_string.rsplit("+", 1)
            if not build_part:
                raise SemverError("Build metadata cannot be empty")
            try:
                build_metadata = _parse_identifier_list(build_part, allow_leading_zero=True)
            except ValueError as e:
                raise SemverError(str(e))

        # Split off prerelease
        prerelease: Optional[Tuple[Union[int, str], ...]] = None
        if "-" in version_string:
            version_string, prerelease_part = version_string.rsplit("-", 1)
            if not prerelease_part:
                raise SemverError("Prerelease cannot be empty")
            try:
                prerelease = _parse_identifier_list(prerelease_part, allow_leading_zero=False)
            except ValueError as e:
                raise SemverError(str(e))

        # Parse major.minor.patch
        parts = version_string.split(".")
        if len(parts) != 3:
            raise SemverError(
                f"Version must have exactly 3 numeric components, got {len(parts)}"
            )

        try:
            major = _parse_numeric(parts[0], allow_leading_zero=False)
            minor = _parse_numeric(parts[1], allow_leading_zero=False)
            patch = _parse_numeric(parts[2], allow_leading_zero=False)
        except ValueError as e:
            raise SemverError(str(e))
        except SemverError:
            raise

        return Version(major, minor, patch, prerelease, build_metadata)

    def bump_major(self) -> "Version":
        """Return a new Version with major incremented and minor/patch reset to 0."""
        return Version(self._major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        """Return a new Version with minor incremented and patch reset to 0."""
        return Version(self._major, self._minor + 1, 0)

    def bump_patch(self) -> "Version":
        """Return a new Version with patch incremented."""
        return Version(self._major, self._minor, self._patch + 1)

    def __eq__(self, other: object) -> bool:
        """Two versions are equal if major, minor, patch, and prerelease match.

        Build metadata is ignored in comparison per semver spec.
        """
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self._major == other._major
            and self._minor == other._minor
            and self._patch == other._patch
            and self._prerelease == other._prerelease
        )

    def __lt__(self, other: object) -> bool:
        """Compare versions per semver 2.0.0 precedence rules."""
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major.minor.patch
        if self._major != other._major:
            return self._major < other._major
        if self._minor != other._minor:
            return self._minor < other._minor
        if self._patch != other._patch:
            return self._patch < other._patch

        # Prerelease comparison
        # Release version > prerelease version
        if self._prerelease is None and other._prerelease is None:
            return False
        if self._prerelease is None:
            return False
        if other._prerelease is None:
            return True

        # Both have prerelease: compare identifiers
        return _compare_prerelease(self._prerelease, other._prerelease) < 0

    def __le__(self, other: object) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Version):
            return NotImplemented
        return self == other or self < other

    def __gt__(self, other: object) -> bool:
        """Greater than comparison."""
        if not isinstance(other, Version):
            return NotImplemented
        return not (self <= other)

    def __ge__(self, other: object) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Version):
            return NotImplemented
        return not (self < other)

    def __ne__(self, other: object) -> bool:
        """Not equal comparison."""
        if not isinstance(other, Version):
            return NotImplemented
        return not (self == other)

    def __str__(self) -> str:
        """Return the string representation of the version."""
        result = f"{self._major}.{self._minor}.{self._patch}"

        if self._prerelease is not None:
            result += "-" + ".".join(str(x) for x in self._prerelease)

        if self._build_metadata is not None:
            result += "+" + ".".join(str(x) for x in self._build_metadata)

        return result

    def __repr__(self) -> str:
        """Return a detailed representation."""
        return f"Version('{str(self)}')"

    def __hash__(self) -> int:
        """Hash based on major, minor, patch, and prerelease (build metadata ignored)."""
        return hash((self._major, self._minor, self._patch, self._prerelease))


def _parse_numeric(s: str, allow_leading_zero: bool) -> int:
    """Parse and validate a numeric version component.

    Args:
        s: The string to parse.
        allow_leading_zero: Whether leading zeros are permitted.

    Returns:
        The parsed integer.

    Raises:
        ValueError: If the string is invalid.
    """
    if not s:
        raise ValueError("Numeric component cannot be empty")

    if not s.isdigit():
        raise ValueError(f"Numeric component must contain only digits, got '{s}'")

    if len(s) > 1 and s[0] == "0" and not allow_leading_zero:
        raise ValueError(f"Leading zeros not allowed in numeric identifier '{s}'")

    return int(s)


def _parse_identifier_list(
    s: str, allow_leading_zero: bool
) -> Tuple[Union[int, str], ...]:
    """Parse a dot-separated list of identifiers (prerelease or build metadata).

    Args:
        s: The string to parse, e.g. 'alpha.1.beta'.
        allow_leading_zero: Whether numeric identifiers can have leading zeros.

    Returns:
        A tuple of identifiers (converted to int if all-digit).

    Raises:
        ValueError: If any identifier is invalid.
    """
    if not s:
        raise ValueError("Identifier list cannot be empty")

    identifiers: list[Union[int, str]] = []

    for part in s.split("."):
        if not part:
            raise ValueError("Identifier cannot be empty")

        # Check for invalid characters (only alphanumerics and hyphens allowed)
        if not all(c.isalnum() or c == "-" for c in part):
            raise ValueError(f"Invalid character in identifier '{part}'")

        # Try to parse as integer if all digits
        if part.isdigit():
            if len(part) > 1 and part[0] == "0" and not allow_leading_zero:
                raise ValueError(f"Leading zeros not allowed in numeric identifier '{part}'")
            identifiers.append(int(part))
        else:
            identifiers.append(part)

    return tuple(identifiers)


def _compare_prerelease(
    pre1: Tuple[Union[int, str], ...], pre2: Tuple[Union[int, str], ...]
) -> int:
    """Compare two prerelease version tuples per semver spec.

    Args:
        pre1: First prerelease tuple.
        pre2: Second prerelease tuple.

    Returns:
        Negative if pre1 < pre2, 0 if equal, positive if pre1 > pre2.
    """
    # Shorter prerelease sorts lower (e.g., 1.0.0-alpha < 1.0.0-alpha.1)
    min_len = min(len(pre1), len(pre2))

    for i in range(min_len):
        id1, id2 = pre1[i], pre2[i]

        # Numeric identifiers always compare lower than non-numeric
        id1_is_int = isinstance(id1, int)
        id2_is_int = isinstance(id2, int)

        if id1_is_int and not id2_is_int:
            return -1
        if not id1_is_int and id2_is_int:
            return 1

        # Both numeric or both string: standard comparison
        if id1 < id2:
            return -1
        if id1 > id2:
            return 1

    # If all compared identifiers are equal, shorter wins
    if len(pre1) < len(pre2):
        return -1
    if len(pre1) > len(pre2):
        return 1

    return 0
