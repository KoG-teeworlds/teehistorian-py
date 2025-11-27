#!/usr/bin/env python3
"""Tests for the validators module."""

import pytest
from teehistorian_py.validators import (
    CLIENT_ID_MAX,
    CLIENT_ID_MIN,
    TEAM_MAX,
    TEAM_MIN,
    ValidationError,
    validate_bytes,
    validate_int,
    validate_list_int,
    validate_str,
    validate_uuid,
)


class TestValidateInt:
    """Tests for validate_int function."""

    def test_validate_int_valid_integer(self):
        """Test validating a valid integer."""
        assert validate_int(5, "value") == 5

    def test_validate_int_string_coercion(self):
        """Test that string integers are coerced."""
        assert validate_int("42", "value") == 42

    def test_validate_int_float_coercion(self):
        """Test that floats are coerced to integers."""
        assert validate_int(5.0, "value") == 5

    def test_validate_int_negative(self):
        """Test validating negative integers."""
        assert validate_int(-10, "value") == -10

    def test_validate_int_zero(self):
        """Test validating zero."""
        assert validate_int(0, "value") == 0

    def test_validate_int_with_min_constraint(self):
        """Test integer validation with minimum constraint."""
        assert validate_int(10, "value", min_val=0) == 10

    def test_validate_int_below_min_raises(self):
        """Test that value below minimum raises ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 0"):
            validate_int(-1, "value", min_val=0)

    def test_validate_int_with_max_constraint(self):
        """Test integer validation with maximum constraint."""
        assert validate_int(10, "value", max_val=20) == 10

    def test_validate_int_above_max_raises(self):
        """Test that value above maximum raises ValidationError."""
        with pytest.raises(ValidationError, match="must be <= 20"):
            validate_int(25, "value", max_val=20)

    def test_validate_int_with_min_and_max(self):
        """Test integer validation with both constraints."""
        assert validate_int(15, "value", min_val=10, max_val=20) == 15

    def test_validate_int_invalid_string_raises(self):
        """Test that invalid string raises ValidationError."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_int("invalid", "value")

    def test_validate_int_invalid_type_raises(self):
        """Test that invalid type raises ValidationError."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_int([], "value")

    def test_validate_int_client_id_valid(self):
        """Test validating client IDs within valid range."""
        assert validate_int(0, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX) == 0
        assert validate_int(31, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX) == 31

    def test_validate_int_team_valid(self):
        """Test validating team IDs within valid range."""
        assert validate_int(0, "team", TEAM_MIN, TEAM_MAX) == 0
        assert validate_int(1, "team", TEAM_MIN, TEAM_MAX) == 1


class TestValidateStr:
    """Tests for validate_str function."""

    def test_validate_str_valid_string(self):
        """Test validating a valid string."""
        assert validate_str("hello", "value") == "hello"

    def test_validate_str_integer_coercion(self):
        """Test that integers are coerced to strings."""
        assert validate_str(123, "value") == "123"

    def test_validate_str_empty_string_allowed(self):
        """Test that empty strings are allowed by default."""
        assert validate_str("", "value") == ""

    def test_validate_str_empty_string_not_allowed(self):
        """Test that empty strings can be disallowed."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_str("", "value", allow_empty=False)

    def test_validate_str_with_min_length(self):
        """Test string validation with minimum length."""
        assert validate_str("hello", "value", min_len=3) == "hello"

    def test_validate_str_below_min_length_raises(self):
        """Test that string below minimum length raises ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 3 characters"):
            validate_str("hi", "value", min_len=3)

    def test_validate_str_with_max_length(self):
        """Test string validation with maximum length."""
        assert validate_str("hello", "value", max_len=10) == "hello"

    def test_validate_str_above_max_length_raises(self):
        """Test that string above maximum length raises ValidationError."""
        with pytest.raises(ValidationError, match="must be <= 3 characters"):
            validate_str("hello", "value", max_len=3)

    def test_validate_str_with_min_and_max_length(self):
        """Test string validation with both length constraints."""
        assert validate_str("hello", "value", min_len=3, max_len=10) == "hello"

    def test_validate_str_player_name_valid(self):
        """Test validating player names."""
        assert validate_str("TestPlayer", "name") == "TestPlayer"

    def test_validate_str_unicode_characters(self):
        """Test validating strings with unicode characters."""
        assert validate_str("Player™©®", "name") == "Player™©®"

    def test_validate_str_special_characters(self):
        """Test validating strings with special characters."""
        assert validate_str("!@#$%^&*()", "name") == "!@#$%^&*()"


class TestValidateBytes:
    """Tests for validate_bytes function."""

    def test_validate_bytes_valid_bytes(self):
        """Test validating valid bytes."""
        data = b"hello"
        assert validate_bytes(data, "data") == data

    def test_validate_bytes_list_coercion(self):
        """Test that list of ints is coerced to bytes."""
        result = validate_bytes([65, 66, 67], "data")
        assert result == b"ABC"

    def test_validate_bytes_bytearray_coercion(self):
        """Test that bytearray is coerced to bytes."""
        ba = bytearray(b"hello")
        result = validate_bytes(ba, "data")
        assert result == b"hello"

    def test_validate_bytes_empty_allowed(self):
        """Test that empty bytes are allowed."""
        assert validate_bytes(b"", "data") == b""

    def test_validate_bytes_with_min_length(self):
        """Test bytes validation with minimum length."""
        assert validate_bytes(b"hello", "data", min_len=3) == b"hello"

    def test_validate_bytes_below_min_length_raises(self):
        """Test that bytes below minimum length raise ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 3 bytes"):
            validate_bytes(b"hi", "data", min_len=3)

    def test_validate_bytes_with_max_length(self):
        """Test bytes validation with maximum length."""
        assert validate_bytes(b"hello", "data", max_len=10) == b"hello"

    def test_validate_bytes_above_max_length_raises(self):
        """Test that bytes above maximum length raise ValidationError."""
        with pytest.raises(ValidationError, match="must be <= 3 bytes"):
            validate_bytes(b"hello", "data", max_len=3)

    def test_validate_bytes_invalid_type_raises(self):
        """Test that invalid type raises ValidationError."""
        with pytest.raises(ValidationError, match="must be bytes"):
            validate_bytes(123, "data")

    def test_validate_bytes_invalid_list_values_raises(self):
        """Test that list with invalid values raises ValidationError."""
        with pytest.raises(ValidationError, match="must be bytes or list of ints"):
            validate_bytes([65, "invalid", 67], "data")


class TestValidateUuid:
    """Tests for validate_uuid function."""

    def test_validate_uuid_valid_uuid_string(self):
        """Test validating a valid UUID string."""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        result = validate_uuid(uuid_str, "uuid")
        assert result == uuid_str

    def test_validate_uuid_nil_uuid(self):
        """Test validating nil UUID."""
        nil_uuid = "00000000-0000-0000-0000-000000000000"
        result = validate_uuid(nil_uuid, "uuid")
        assert result == nil_uuid

    def test_validate_uuid_uppercase_to_lowercase(self):
        """Test that UUID is converted to lowercase."""
        uuid_str = "550E8400-E29B-41D4-A716-446655440000"
        result = validate_uuid(uuid_str, "uuid")
        assert result == "550e8400-e29b-41d4-a716-446655440000"

    def test_validate_uuid_invalid_format_raises(self):
        """Test that invalid UUID format raises ValidationError."""
        with pytest.raises(ValidationError, match="must be in UUID format"):
            validate_uuid("not-a-uuid", "uuid")

    def test_validate_uuid_wrong_segment_count_raises(self):
        """Test that UUID with wrong segment count raises ValidationError."""
        with pytest.raises(ValidationError, match="must be in UUID format"):
            validate_uuid("12345678-1234-5678-1234", "uuid")

    def test_validate_uuid_non_hex_characters_raises(self):
        """Test that non-hex characters in UUID raise ValidationError."""
        with pytest.raises(ValidationError, match="must contain only hex digits"):
            validate_uuid("zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz", "uuid")

    def test_validate_uuid_wrong_segment_length_raises(self):
        """Test that wrong segment lengths raise ValidationError."""
        with pytest.raises(ValidationError, match="must be in UUID format"):
            validate_uuid("1234567-1234-5678-1234-567812345678", "uuid")


class TestValidateListInt:
    """Tests for validate_list_int function."""

    def test_validate_list_int_valid_list(self):
        """Test validating a valid list of integers."""
        result = validate_list_int([1, 2, 3], "values")
        assert result == [1, 2, 3]

    def test_validate_list_int_string_coercion(self):
        """Test that strings in list are coerced to integers."""
        result = validate_list_int(["1", "2", "3"], "values")
        assert result == [1, 2, 3]

    def test_validate_list_int_mixed_types(self):
        """Test that mixed int and string types are coerced."""
        result = validate_list_int([1, "2", 3], "values")
        assert result == [1, 2, 3]

    def test_validate_list_int_empty_list(self):
        """Test validating empty list."""
        result = validate_list_int([], "values")
        assert result == []

    def test_validate_list_int_tuple_input(self):
        """Test that tuples are accepted."""
        result = validate_list_int((1, 2, 3), "values")
        assert result == [1, 2, 3]

    def test_validate_list_int_invalid_element_raises(self):
        """Test that invalid element in list raises ValidationError."""
        with pytest.raises(ValidationError, match="must contain only integers"):
            validate_list_int([1, "invalid", 3], "values")

    def test_validate_list_int_not_list_raises(self):
        """Test that non-list input raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a list"):
            validate_list_int("not a list", "values")


class TestValidationConstants:
    """Tests for validation constants."""

    def test_client_id_constants_exist(self):
        """Test that client ID constants are defined."""
        assert isinstance(CLIENT_ID_MIN, int)
        assert isinstance(CLIENT_ID_MAX, int)
        assert CLIENT_ID_MIN < CLIENT_ID_MAX

    def test_team_constants_exist(self):
        """Test that team constants are defined."""
        assert isinstance(TEAM_MIN, int)
        assert isinstance(TEAM_MAX, int)
        assert TEAM_MIN < TEAM_MAX

    def test_client_id_range(self):
        """Test that client ID range is reasonable."""
        assert CLIENT_ID_MIN >= 0
        assert CLIENT_ID_MAX <= 255

    def test_team_range(self):
        """Test that team range is reasonable."""
        assert TEAM_MIN >= 0
        assert TEAM_MAX <= 255
