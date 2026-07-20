"""Development tooling for the template repository itself."""

from pathlib import Path

PROJECT_ROOT_DIRECTORY = Path(__file__).resolve().parent.parent


def emojize_message(message: str, *, success: bool = True) -> str:
    """Render a pass/fail banner consistent with the generated project's output."""
    return f'✅ {message} 👍' if success else f'❌ {message} 👎'
