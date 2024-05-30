#!/usr/bin/env python3
"""Handles password hashing."""

import bcrypt


def hash_password(password: str) -> bytes:
    """Hashes a password with salt using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """Checks if a password matches a hashed password."""
    return bcrypt.checkpw(password.encode(), hashed_password)