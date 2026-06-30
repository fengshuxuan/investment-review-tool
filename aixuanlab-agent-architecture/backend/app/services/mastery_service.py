from collections import Counter, defaultdict
from typing import Any


class MasteryService:
    """Calculate function mastery from practice attempts."""

    def calculate_mastery(self, attempts: list[dict[str, Any]]) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for attempt in attempts:
            for fn in attempt.get("function_tags", []) or []:
                grouped[fn].append(attempt)

        result: dict[str, Any] = {}
        for fn, rows in grouped.items():
            total = len(rows)
            correct = sum(1 for row in rows if row.get("is_correct"))
            recent = rows[-5:]
            recent_correct = sum(1 for row in recent if row.get("is_correct"))
            error_counter = Counter(row.get("error_type") for row in rows if row.get("error_type"))
            accuracy = correct / total if total else 0
            recent_accuracy = recent_correct / len(recent) if recent else 0
            mastery_score = round(accuracy * 50 + recent_accuracy * 30 + min(total, 10))
            result[fn] = {
                "total_attempts": total,
                "correct_attempts": correct,
                "accuracy_rate": accuracy,
                "recent_accuracy_rate": recent_accuracy,
                "common_error_types": error_counter.most_common(3),
                "mastery_score": min(mastery_score, 100),
                "mastery_level": self._level(mastery_score),
            }
        return result

    @staticmethod
    def _level(score: int) -> str:
        if score >= 85:
            return "熟练"
        if score >= 65:
            return "基本掌握"
        if score >= 35:
            return "练习中"
        return "未入门"
