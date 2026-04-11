"""Comprehensive tests for semverlite library."""

import pytest
from semverlite import Version, SemverError


class TestVersionParsing:
    """Test Version.parse() for valid inputs."""

    def test_parse_basic_version_string(self):
        """Parse basic semantic version like 1.2.3."""
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease is None
        assert v.build_metadata is None

    def test_parse_version_with_prerelease(self):
        """Parse version with prerelease identifier like 1.2.3-alpha."""
        v = Version.parse("1.2.3-alpha")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease == ("alpha",)

    def test_parse_version_with_prerelease_numeric(self):
        """Parse version with numeric prerelease like 1.2.3-1."""
        v = Version.parse("1.2.3-1")
        assert v.prerelease == (1,)

    def test_parse_version_with_dotted_prerelease(self):
        """Parse version with dotted prerelease like 1.2.3-alpha.1."""
        v = Version.parse("1.2.3-alpha.1")
        assert v.prerelease == ("alpha", 1)

    def test_parse_version_with_complex_prerelease(self):
        """Parse version with complex prerelease like 1.2.3-alpha.1.beta.2."""
        v = Version.parse("1.2.3-alpha.1.beta.2")
        assert v.prerelease == ("alpha", 1, "beta", 2)

    def test_parse_version_with_build_metadata(self):
        """Parse version with build metadata like 1.2.3+build.123."""
        v = Version.parse("1.2.3+build.123")
        assert v.build_metadata == ("build", 123)

    def test_parse_version_with_prerelease_and_build(self):
        """Parse version with both prerelease and build metadata."""
        v = Version.parse("1.2.3-alpha.1+build.456")
        assert v.prerelease == ("alpha", 1)
        assert v.build_metadata == ("build", 456)

    def test_parse_zero_version(self):
        """Parse 0.0.0 version."""
        v = Version.parse("0.0.0")
        assert v.major == 0
        assert v.minor == 0
        assert v.patch == 0

    def test_parse_large_version_numbers(self):
        """Parse version with large numbers like 999.999.999."""
        v = Version.parse("999.999.999")
        assert v.major == 999
        assert v.minor == 999
        assert v.patch == 999

    def test_parse_complex_prerelease_numeric_first(self):
        """Parse version with numeric identifier first in prerelease."""
        v = Version.parse("1.0.0-1.alpha")
        assert v.prerelease == (1, "alpha")


class TestVersionParsingErrors:
    """Test Version.parse() error handling for invalid inputs."""

    def test_parse_empty_string_raises_error(self):
        """Parsing empty string raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("")

    def test_parse_non_string_input_raises_error(self):
        """Parsing non-string input raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse(123)

    def test_parse_missing_minor_raises_error(self):
        """Parsing missing minor version like '1' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1")

    def test_parse_missing_patch_raises_error(self):
        """Parsing missing patch version like '1.2' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2")

    def test_parse_extra_components_raises_error(self):
        """Parsing extra components like '1.2.3.4' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.3.4")

    def test_parse_non_numeric_major_raises_error(self):
        """Parsing non-numeric major version raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("a.2.3")

    def test_parse_non_numeric_minor_raises_error(self):
        """Parsing non-numeric minor version raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.b.3")

    def test_parse_non_numeric_patch_raises_error(self):
        """Parsing non-numeric patch version raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.c")

    def test_parse_leading_zero_in_major_raises_error(self):
        """Parsing leading zero in major raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("01.2.3")

    def test_parse_leading_zero_in_minor_raises_error(self):
        """Parsing leading zero in minor raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.02.3")

    def test_parse_leading_zero_in_patch_raises_error(self):
        """Parsing leading zero in patch raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.03")

    def test_parse_empty_prerelease_raises_error(self):
        """Parsing empty prerelease like '1.2.3-' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.3-")

    def test_parse_empty_build_metadata_raises_error(self):
        """Parsing empty build metadata like '1.2.3+' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.3+")

    def test_parse_empty_prerelease_identifier_raises_error(self):
        """Parsing empty identifier in prerelease like '1.2.3-alpha..1' raises SemverError."""
        with pytest.raises(SemverError):
            Version.parse("1.2.3-alpha..1")


class TestVersionComparison:
    """Test comparison operators."""

    def test_version_equality_same_version(self):
        """Same versions are equal."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.3")
        assert v1 == v2

    def test_version_inequality_different_major(self):
        """Versions with different major are not equal."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("2.2.3")
        assert v1 != v2

    def test_version_less_than_major(self):
        """Version with lower major is less."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("2.2.3")
        assert v1 < v2

    def test_version_less_than_minor(self):
        """Version with lower minor is less."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.3.3")
        assert v1 < v2

    def test_version_less_than_patch(self):
        """Version with lower patch is less."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.4")
        assert v1 < v2

    def test_version_greater_than(self):
        """Greater than comparison works."""
        v1 = Version.parse("2.2.3")
        v2 = Version.parse("1.2.3")
        assert v1 > v2

    def test_version_less_equal_equal(self):
        """Less than or equal works for equal versions."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.3")
        assert v1 <= v2

    def test_version_less_equal_less(self):
        """Less than or equal works for lesser version."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.4")
        assert v1 <= v2

    def test_version_greater_equal_equal(self):
        """Greater than or equal works for equal versions."""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.3")
        assert v1 >= v2

    def test_version_greater_equal_greater(self):
        """Greater than or equal works for greater version."""
        v1 = Version.parse("1.2.4")
        v2 = Version.parse("1.2.3")
        assert v1 >= v2

    def test_prerelease_less_than_release(self):
        """Prerelease version is less than release version."""
        v1 = Version.parse("1.0.0-alpha")
        v2 = Version.parse("1.0.0")
        assert v1 < v2

    def test_prerelease_ordering_numeric_before_alpha(self):
        """Numeric prerelease identifiers sort before alphanumeric."""
        v1 = Version.parse("1.0.0-1")
        v2 = Version.parse("1.0.0-alpha")
        assert v1 < v2

    def test_prerelease_ordering_fewer_fields_before_more(self):
        """Fewer prerelease identifiers sort before more."""
        v1 = Version.parse("1.0.0-alpha")
        v2 = Version.parse("1.0.0-alpha.1")
        assert v1 < v2

    def test_prerelease_ordering_numeric_comparison(self):
        """Numeric prerelease identifiers compared as integers."""
        v1 = Version.parse("1.0.0-1")
        v2 = Version.parse("1.0.0-2")
        assert v1 < v2

    def test_prerelease_ordering_string_comparison(self):
        """Alphanumeric prerelease identifiers compared as strings."""
        v1 = Version.parse("1.0.0-alpha")
        v2 = Version.parse("1.0.0-beta")
        assert v1 < v2

    def test_build_metadata_ignored_in_comparison(self):
        """Build metadata is ignored in comparison."""
        v1 = Version.parse("1.2.3+build.1")
        v2 = Version.parse("1.2.3+build.2")
        assert v1 == v2

    def test_build_metadata_different_versions_still_different(self):
        """Different versions with build metadata are still different."""
        v1 = Version.parse("1.2.3+build.1")
        v2 = Version.parse("1.2.4+build.1")
        assert v1 != v2


class TestVersionProperties:
    """Test Version properties and methods."""

    def test_is_stable_for_release_version(self):
        """Release version has is_stable True."""
        v = Version.parse("1.2.3")
        assert v.is_stable is True

    def test_is_stable_for_prerelease_version(self):
        """Prerelease version has is_stable False."""
        v = Version.parse("1.2.3-alpha")
        assert v.is_stable is False

    def test_is_stable_for_version_with_only_build(self):
        """Version with only build metadata has is_stable True."""
        v = Version.parse("1.2.3+build.123")
        assert v.is_stable is True


class TestVersionBumping:
    """Test Version bumping methods."""

    def test_bump_major(self):
        """Bump major increments major and zeros minor and patch."""
        v = Version.parse("1.2.3")
        bumped = v.bump_major()
        assert bumped.major == 2
        assert bumped.minor == 0
        assert bumped.patch == 0
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_bump_minor(self):
        """Bump minor increments minor and zeros patch."""
        v = Version.parse("1.2.3")
        bumped = v.bump_minor()
        assert bumped.major == 1
        assert bumped.minor == 3
        assert bumped.patch == 0
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_bump_patch(self):
        """Bump patch increments patch."""
        v = Version.parse("1.2.3")
        bumped = v.bump_patch()
        assert bumped.major == 1
        assert bumped.minor == 2
        assert bumped.patch == 4
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_bump_major_from_prerelease(self):
        """Bump major from prerelease version."""
        v = Version.parse("1.2.3-alpha.1")
        bumped = v.bump_major()
        assert bumped.major == 2
        assert bumped.minor == 0
        assert bumped.patch == 0
        assert bumped.prerelease is None

    def test_bump_minor_from_prerelease(self):
        """Bump minor from prerelease version."""
        v = Version.parse("1.2.3-alpha.1")
        bumped = v.bump_minor()
        assert bumped.major == 1
        assert bumped.minor == 3
        assert bumped.patch == 0
        assert bumped.prerelease is None

    def test_bump_patch_from_prerelease(self):
        """Bump patch from prerelease version."""
        v = Version.parse("1.2.3-alpha.1")
        bumped = v.bump_patch()
        assert bumped.major == 1
        assert bumped.minor == 2
        assert bumped.patch == 4
        assert bumped.prerelease is None

    def test_bumped_version_is_immutable(self):
        """Original version unchanged after bumping."""
        v = Version.parse("1.2.3")
        bumped = v.bump_major()
        assert v.major == 1
        assert bumped.major == 2


class TestVersionStringRepresentation:
    """Test Version string representation."""

    def test_str_basic_version(self):
        """String representation of basic version."""
        v = Version.parse("1.2.3")
        assert str(v) == "1.2.3"

    def test_str_version_with_prerelease(self):
        """String representation with prerelease."""
        v = Version.parse("1.2.3-alpha.1")
        assert str(v) == "1.2.3-alpha.1"

    def test_str_version_with_build(self):
        """String representation with build metadata."""
        v = Version.parse("1.2.3+build.456")
        assert str(v) == "1.2.3+build.456"

    def test_str_version_with_prerelease_and_build(self):
        """String representation with both prerelease and build."""
        v = Version.parse("1.2.3-alpha.1+build.456")
        assert str(v) == "1.2.3-alpha.1+build.456"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_version_with_only_build_metadata(self):
        """Parse version with only build metadata (no prerelease)."""
        v = Version.parse("1.0.0+build.1")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0
        assert v.prerelease is None
        assert v.build_metadata == ("build", 1)

    def test_large_prerelease_numeric_identifiers(self):
        """Parse large numeric identifiers in prerelease."""
        v = Version.parse("1.0.0-999.888.777")
        assert v.prerelease == (999, 888, 777)

    def test_mixed_case_build_metadata(self):
        """Build metadata identifiers case-sensitive."""
        v = Version.parse("1.0.0+BUILD.123")
        assert v.build_metadata == ("BUILD", 123)

    def test_prerelease_all_numeric(self):
        """Prerelease with all numeric identifiers."""
        v = Version.parse("1.0.0-1.2.3")
        assert v.prerelease == (1, 2, 3)

    def test_version_zero_zero_zero(self):
        """Version 0.0.0 is valid."""
        v = Version.parse("0.0.0")
        assert v.major == 0
        assert v.minor == 0
        assert v.patch == 0

    def test_inequality_chain_comparison(self):
        """Multiple comparisons in sequence."""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("2.0.0")
        v3 = Version.parse("3.0.0")
        assert v1 < v2 < v3

    def test_prerelease_with_numeric_starting_zero(self):
        """Numeric identifier starting with zero should fail."""
        with pytest.raises(SemverError):
            Version.parse("1.0.0-01")

    def test_invalid_character_in_prerelease(self):
        """Invalid character in prerelease identifier."""
        with pytest.raises(SemverError):
            Version.parse("1.0.0-alpha@")

    def test_invalid_character_in_build(self):
        """Invalid character in build metadata identifier."""
        with pytest.raises(SemverError):
            Version.parse("1.0.0+build#123")
