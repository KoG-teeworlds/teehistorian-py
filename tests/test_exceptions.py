#!/usr/bin/env python3
"""Tests for the exceptions module."""

import pytest
from teehistorian_py.exceptions import TeehistorianError


class TestTeehistorianError:
    """Tests for TeehistorianError exception."""

    def test_teehistorian_error_is_exception(self):
        """Test that TeehistorianError is an Exception subclass."""
        assert issubclass(TeehistorianError, Exception)

    def test_teehistorian_error_can_be_raised(self):
        """Test that TeehistorianError can be raised."""
        with pytest.raises(TeehistorianError):
            raise TeehistorianError("Test error")

    def test_teehistorian_error_with_message(self):
        """Test that TeehistorianError preserves message."""
        message = "Something went wrong"
        with pytest.raises(TeehistorianError, match=message):
            raise TeehistorianError(message)

    def test_teehistorian_error_str_representation(self):
        """Test string representation of TeehistorianError."""
        error = TeehistorianError("Test message")
        assert "Test message" in str(error)

    def test_teehistorian_error_inheritance(self):
        """Test that TeehistorianError can be caught as Exception."""
        try:
            raise TeehistorianError("test")
        except Exception as e:
            assert isinstance(e, TeehistorianError)

    def test_teehistorian_error_with_args(self):
        """Test TeehistorianError with multiple arguments."""
        error = TeehistorianError("arg1", "arg2")
        assert "arg1" in str(error)

    def test_teehistorian_error_empty(self):
        """Test TeehistorianError with no message."""
        error = TeehistorianError()
        assert isinstance(error, Exception)

    def test_teehistorian_error_chaining(self):
        """Test exception chaining with TeehistorianError."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise TeehistorianError("Wrapped error") from e
        except TeehistorianError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)

    def test_teehistorian_error_context(self):
        """Test exception context with TeehistorianError."""
        try:
            raise ValueError("First error")
        except ValueError:
            try:
                raise TeehistorianError("Second error")
            except TeehistorianError as e:
                assert e.__context__ is not None
                assert isinstance(e.__context__, ValueError)
