# -*- coding: utf-8 -*-
"""觉知日记服务通用工具。"""

from __future__ import annotations

import json
import secrets

from fastapi import HTTPException, status

from .constants import BINDING_CODE_ALPHABET, BINDING_CODE_LENGTH


def _normalize_content(content: str) -> str:
    normalized = content.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容不能为空",
        )
    return normalized


def _generate_binding_code() -> str:
    return "".join(
        secrets.choice(BINDING_CODE_ALPHABET) for _ in range(BINDING_CODE_LENGTH)
    )


def _json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _json_loads(raw: str, fallback: object) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def _json_loads_list(raw: str) -> list[object]:
    value = _json_loads(raw, [])
    return value if isinstance(value, list) else []
