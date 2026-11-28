from typing import Protocol, Literal, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):
    def generate_json(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
        model_role: Literal["strong", "fast"],
    ) -> T:
        """Generates structured JSON adhering to the given Pydantic schema."""
        ...
