"""
Допоміжні функції.
"""

import re


def split_long_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Розбиває довге повідомлення на частини по `max_length` символів,
    намагаючись різати по межі абзацу / речення.
    """
    if len(text) <= max_length:
        return [text]

    parts: list[str] = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        # шукаємо останній перенос рядка або пробіл перед лімітом
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = text.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length

        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    return parts


def escape_markdown(text: str) -> str:
    """Екранує спеціальні символи MarkdownV2."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)


def truncate_history(
    messages: list[dict],
    max_pairs: int,
) -> list[dict]:
    """
    Обрізає історію, залишаючи останні `max_pairs` пар (user+assistant).
    Системний промпт (якщо є) завжди зберігається першим.
    """
    if len(messages) <= 1:
        return messages

    system = messages[0] if messages[0].get("role") == "system" else None
    history = messages[1:] if system else messages[:]

    # видаляємо зайві пари з початку
    while len(history) > max_pairs * 2:
        history.pop(0)

    return ([system] + history) if system else history
