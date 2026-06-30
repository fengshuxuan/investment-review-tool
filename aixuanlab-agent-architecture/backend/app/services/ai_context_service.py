from typing import Any


class AIContextService:
    """Build the compact learning context passed to the model.

    Replace the placeholder methods with real database queries from the existing aixuanlab backend.
    """

    def build_context(
        self,
        user_id: str,
        current_practice_id: str | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "user_profile": self.get_user_profile(user_id),
            "recent_practice_history": self.get_recent_practice_history(user_id),
            "mastery_snapshot": self.get_mastery_snapshot(user_id),
            "learning_memories": self.get_relevant_memories(user_id, current_practice_id),
            "current_practice": self.get_current_practice(current_practice_id),
            "conversation_summary": self.get_conversation_summary(conversation_id),
        }

    def get_user_profile(self, user_id: str) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "excel_level": "beginner",
            "target_role": None,
            "learning_goal": None,
            "preferred_explanation_style": "先给提示，再给答案",
        }

    def get_recent_practice_history(self, user_id: str) -> list[dict[str, Any]]:
        return []

    def get_mastery_snapshot(self, user_id: str) -> dict[str, Any]:
        return {
            "weak_functions": [],
            "strong_functions": [],
            "function_scores": {},
        }

    def get_relevant_memories(self, user_id: str, current_practice_id: str | None = None) -> list[dict[str, Any]]:
        return []

    def get_current_practice(self, practice_id: str | None) -> dict[str, Any] | None:
        if not practice_id:
            return None
        return {"practice_id": practice_id}

    def get_conversation_summary(self, conversation_id: str | None) -> str | None:
        return None
