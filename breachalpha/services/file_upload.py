"""File upload service.

Handles streaming file upload with size limits and temp file management.
Eliminates duplicated upload logic from 4 route handlers.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import AsyncIterator

from fastapi import HTTPException, UploadFile

from ..core.constants import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_BYTES

logger = logging.getLogger(__name__)


def validate_upload_extension(filename: str | None) -> str:
    """Validate file extension against allowed types.

    Args:
        filename: The uploaded file's name.

    Returns:
        The validated extension (e.g., '.csv').

    Raises:
        HTTPException: If file type is not allowed.
    """
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}",
        )
    return suffix


async def save_upload(file: UploadFile, suffix: str) -> Path:
    """Stream uploaded file to a temp location with size enforcement.

    Args:
        file: The FastAPI UploadFile object.
        suffix: File extension (e.g., '.csv').

    Returns:
        Path to the saved temp file.

    Raises:
        HTTPException: If file exceeds MAX_UPLOAD_BYTES.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = Path(tmp.name)
    try:
        total_size = 0
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum upload size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
                )
            tmp.write(chunk)
    finally:
        tmp.close()
    return tmp_path


def cleanup_upload(tmp_path: Path | None) -> None:
    """Remove temp file if it exists. Safe to call with None."""
    if tmp_path and tmp_path.exists():
        os.unlink(tmp_path)
