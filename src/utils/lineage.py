from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from src.utils.config import settings


def record_lineage(stage: str, payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(settings.lineage_path), exist_ok=True)
    event = {
        'ts_utc': datetime.now(timezone.utc).isoformat(),
        'stage': stage,
        **payload,
    }
    with open(settings.lineage_path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(event) + '\n')
