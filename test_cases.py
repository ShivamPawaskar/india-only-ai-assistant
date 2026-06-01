"""Offline tests for the India-Only AI Assistant project."""

import unittest
from unittest.mock import patch

import india_assistant


REFUSAL_STRING = "I am sorry, I can only talk about India."


class IndiaAssistantTest(unittest.TestCase):
    """Tests assistant behavior without making real API calls."""

    def test_india_capital(self) -> None:
        """India questions should return a real answer."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value="New Delhi is the capital of India."):
                    response = india_assistant.ask("What is the capital of India?")
        self.assertNotEqual(response, REFUSAL_STRING)

    def test_india_history(self) -> None:
        """India history questions should return a real answer."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value="Akbar was a Mughal emperor."):
                    response = india_assistant.ask("Who was Akbar?")
        self.assertNotEqual(response, REFUSAL_STRING)

    def test_non_india_london(self) -> None:
        """Non-India London questions should return the exact refusal."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value=REFUSAL_STRING):
                    response = india_assistant.ask("Tell me about the history of London.")
        self.assertEqual(response, REFUSAL_STRING)

    def test_non_india_us_president(self) -> None:
        """Non-India US president questions should return the exact refusal."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value=REFUSAL_STRING):
                    response = india_assistant.ask("Who is the President of the United States?")
        self.assertEqual(response, REFUSAL_STRING)

    def test_india_festival(self) -> None:
        """India festival questions should return a real answer."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value="Diwali and Holi are major Indian festivals."):
                    response = india_assistant.ask("What are the major festivals of India?")
        self.assertNotEqual(response, REFUSAL_STRING)

    def test_non_india_eiffel(self) -> None:
        """Non-India Eiffel Tower questions should return the exact refusal."""
        with patch("india_assistant.load_env_file", return_value=None):
            with patch.dict("os.environ", {"ASSISTANT_PROVIDER": "opencode", "OPENCODE_API_KEY": "test"}):
                with patch("india_assistant.openai_compatible_chat", return_value=REFUSAL_STRING):
                    response = india_assistant.ask("What is the Eiffel Tower?")
        self.assertEqual(response, REFUSAL_STRING)


if __name__ == "__main__":
    unittest.main()
