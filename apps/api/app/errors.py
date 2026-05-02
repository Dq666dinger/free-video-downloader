from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    status_code: int
    code: str
    message: str

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message}

