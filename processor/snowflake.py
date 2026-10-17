"""Ryuuganime Snowflake ID implementation (SNOWFLAKE_SPEC v0).

Replaces ULID across AnimeAPI. A snowflake is a 128-bit, time-ordered identifier
presented as a 22-char Base64-sortable string (padded form) for DB storage and
API exchange. Always padded to 22 characters.

Spec: https://github.com/ryuuganime/snowflake/raw/refs/heads/main/SNOWFLAKE_SPEC.md
"""

from __future__ import annotations

import hashlib
import threading
import time
from typing import Any

from pydantic_core import core_schema

# Epoch: 2026-07-01T00:00:00Z in Unix milliseconds.
RYUUGANIME_EPOCH = 1_782_864_000_000
SPEC_VERSION = 0  # 3 bits (0b000)
MOD_64_BIT = 1 << 64
MASK_64_BIT = MOD_64_BIT - 1
UINT128 = 1 << 128

# Base64 sortable alphabet (64 symbols, ascending ASCII/UTF-8 codepoint).
# '0'-'9'=48-57, '='=61, 'A'-'Z'=65-90, '_'=95, 'a'-'z'=97-122. Case-sensitive.
BASE64_ALPHABET = "0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
BASE64_CHAR_TO_VAL = {ch: i for i, ch in enumerate(BASE64_ALPHABET)}
PADDED_LEN = 22

# Type / subtype registry (Section 6).
TYPE_MAPPINGS = 8
SUBTYPE_MAPPING = 1


def compute_node_fingerprint(system_identity: str) -> int:
    """Computes a 64-bit node fingerprint using SHA-256 modulo 2^64."""
    sha256_hash = hashlib.sha256(system_identity.encode("utf-8")).digest()
    return int.from_bytes(sha256_hash, byteorder="big") % MOD_64_BIT


def encode_base64(num: int, pad: bool = True) -> str:
    """Encodes a 128-bit integer to a Base64-sortable string.

    With ``pad=True`` returns exactly 22 chars left-padded with ``0`` (DB/storage
    form; lexicographic bytewise order equals uint128 order). With ``pad=False``
    returns the trimmed 1-22 char client-display form.
    """
    if num < 0 or num >= UINT128:
        raise ValueError("Cannot encode numbers outside 128-bit unsigned range.")
    if num == 0:
        return BASE64_ALPHABET[0] * PADDED_LEN if pad else BASE64_ALPHABET[0]
    chars = []
    while num > 0:
        num, rem = divmod(num, 64)
        chars.append(BASE64_ALPHABET[rem])
    b64_str = "".join(reversed(chars))
    return b64_str.rjust(PADDED_LEN, BASE64_ALPHABET[0]) if pad else b64_str


def decode_base64(b64_str: str) -> int:
    """Decodes a Base64-sortable string (1-22 chars, padded or trimmed) to uint128."""
    if not b64_str or not (1 <= len(b64_str) <= PADDED_LEN):
        raise ValueError(
            f"Base64 Snowflake string must be 1-{PADDED_LEN} characters long."
        )
    padded = b64_str.rjust(PADDED_LEN, BASE64_ALPHABET[0])
    num = 0
    for char in padded:
        val = BASE64_CHAR_TO_VAL.get(char)
        if val is None:
            raise ValueError(f"Invalid Base64 character: '{char}'")
        num = num * 64 + val
    if num >= UINT128:
        raise ValueError("Decoded Base64 integer exceeds 128-bit unsigned range.")
    return num


def parse(snowflake_val: str | int | bytes) -> dict[str, int]:
    """Parses a Base64 string, raw 128-bit int, or 16-byte binary into components.

    Returns ``timestamp`` as an absolute Unix millisecond timestamp (UTC).
    """
    if isinstance(snowflake_val, str):
        num = decode_base64(snowflake_val)
    elif isinstance(snowflake_val, bytes):
        if len(snowflake_val) != 16:
            raise ValueError("Snowflake bytes must be exactly 16 bytes long.")
        num = int.from_bytes(snowflake_val, byteorder="big")
    elif isinstance(snowflake_val, int):
        if not (0 <= snowflake_val < UINT128):
            raise ValueError("Snowflake integer must fit within 128 bits unsigned.")
        num = snowflake_val
    else:
        raise TypeError("Snowflake value must be a str, int, or bytes.")

    return {
        "version": (num >> 125) & 0x7,
        "timestamp": ((num >> 83) & 0x3FFFFFFFFFF) + RYUUGANIME_EPOCH,
        "type": (num >> 78) & 0x1F,
        "subtype": (num >> 74) & 0xF,
        "sequence": (num >> 64) & 0x3FF,
        "node_fingerprint": num & MASK_64_BIT,
    }


class RyuuganimeSnowflake:
    """Simple thread-safe snowflake generator."""

    def __init__(
        self, system_identity: str | None = None, raw_fingerprint: int | None = None
    ):
        if raw_fingerprint is not None:
            self.node_fingerprint = raw_fingerprint % MOD_64_BIT
        elif system_identity is not None:
            self.node_fingerprint = compute_node_fingerprint(system_identity)
        else:
            raise ValueError("Must provide system_identity or raw_fingerprint.")

        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def generate_raw(
        self,
        type_id: int,
        subtype_id: int,
        current_ts: int | None = None,
        version: int = SPEC_VERSION,
    ) -> int:
        if not (0 <= version <= 7):
            raise ValueError("Version must be 0-7 (3 bits).")
        if not (0 <= type_id <= 31):
            raise ValueError("Type ID must be 0-31 (5 bits).")
        if not (0 <= subtype_id <= 15):
            raise ValueError("Subtype ID must be 0-15 (4 bits).")

        with self._lock:
            ts = current_ts if current_ts is not None else int(time.time() * 1000)
            if ts == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0x3FF
                if self.sequence == 0:
                    while ts <= self.last_timestamp:
                        time.sleep(0.001)
                        ts = int(time.time() * 1000)
                    self.sequence = 0
            else:
                self.sequence = 0
                self.last_timestamp = ts

            time_diff = ts - RYUUGANIME_EPOCH
            if time_diff < 0 or time_diff >= (1 << 42):
                raise ValueError("Timestamp out of Ryuuganime epoch range.")

            return (
                (version << 125)
                | (time_diff << 83)
                | (type_id << 78)
                | (subtype_id << 74)
                | (self.sequence << 64)
                | self.node_fingerprint
            )

    def generate(
        self,
        type_id: int,
        subtype_id: int,
        current_ts: int | None = None,
        pad: bool = True,
        version: int = SPEC_VERSION,
    ) -> str:
        return encode_base64(
            self.generate_raw(
                type_id=type_id,
                subtype_id=subtype_id,
                current_ts=current_ts,
                version=version,
            ),
            pad=pad,
        )


# Default generator used by convenience helpers.
default_generator = RyuuganimeSnowflake(system_identity="animeapi")


def generate_mapping(current_ts: int | None = None, pad: bool = True) -> str:
    """Generate a padded snowflake for type=8 (MAPPINGS), subtype=1 (MAPPING)."""
    return default_generator.generate(
        type_id=TYPE_MAPPINGS,
        subtype_id=SUBTYPE_MAPPING,
        current_ts=current_ts,
        pad=pad,
    )


def _validate_snowflake(v: Any) -> str:
    """Pydantic validator: normalizes str/int/bytes to the padded 22-char form."""
    if isinstance(v, bytes):
        num = int.from_bytes(v, byteorder="big")
    elif isinstance(v, bool):
        raise TypeError("Snowflake value must be a str, int, or bytes, not bool.")
    elif isinstance(v, int):
        num = v
    elif isinstance(v, str):
        num = decode_base64(v)
    else:
        raise TypeError("Snowflake value must be a str, int, or bytes.")

    if not (0 <= num < UINT128):
        raise ValueError("Snowflake integer must fit within 128 bits unsigned.")
    return encode_base64(num, pad=True)


class SnowflakeId(str):
    """Pydantic-compatible snowflake type. Always padded to 22 chars."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[SnowflakeId], handler: core_schema.GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            _validate_snowflake,
            serialization=core_schema.to_string_ser_schema(),
        )
