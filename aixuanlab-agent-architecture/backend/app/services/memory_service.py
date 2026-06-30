from typing import Any


class MemoryService:
    """Learning memory rules.

    Real implementation should read practice_attempts and user_function_mastery,
    then write learning_memories.
    """

    def generate_candidate_memories(self, user_id: str, recent_attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        # TODO: Aggregate recent attempts by function and error_type.
        return candidates

    def should_save_memory(self, candidate: dict[str, Any]) -> bool:
        return float(candidate.get("confidence", 0)) >= 0.75

    def get_relevant_memories(self, user_id: str, keywords: list[str] | None = None) -> list[dict[str, Any]]:
        return []
