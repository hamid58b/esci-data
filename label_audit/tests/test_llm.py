import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Keep the unit test independent of optional local package installs. The real
# client object is patched in each test before it is used.
sys.modules.setdefault("openai", SimpleNamespace(OpenAI=Mock()))

import config  # noqa: E402
from src.llm import LLMClient  # noqa: E402


def make_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ],
    )


class LLMClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt_file = tempfile.NamedTemporaryFile("w", delete=False)
        self.prompt_file.write(
            "Query: {query}\n"
            "Title: {product_title}\n"
            "Description: {product_description}\n"
            "Bullets: {product_bullet_point}"
        )
        self.prompt_file.close()
        self.prompt_path = Path(self.prompt_file.name)

        self.openai_patcher = patch("src.llm.OpenAI")
        self.openai_cls = self.openai_patcher.start()
        self.addCleanup(self.openai_patcher.stop)
        self.addCleanup(self.prompt_path.unlink)

        self.mock_openai = Mock()
        self.openai_cls.return_value = self.mock_openai

    def test_success(self) -> None:
        expected_payload = {"accurate": False, "reformulated_query": "aa batteries"}
        self.mock_openai.chat.completions.create.return_value = make_response(
            json.dumps(expected_payload)
        )

        client = LLMClient(model=config.MODEL_NAME, prompt_path=self.prompt_path)
        result = client.audit_pair(
            query="aa batteries 100 pack",
            product_title="AA 24 pack",
            product_description=None,
            product_bullet_point="Long lasting",
        )

        self.assertEqual(
            result,
            {"accurate": False, "reformulated_query": "aa batteries"},
        )
        self.mock_openai.chat.completions.create.assert_called_once_with(
            model=config.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Query: aa batteries 100 pack\n"
                        "Title: AA 24 pack\n"
                        "Description: \n"
                        "Bullets: Long lasting"
                    ),
                }
            ],
            temperature=config.TEMPERATURE,
            response_format={"type": "json_object"},
        )

    def test_retries_invalid_json(self) -> None:
        self.mock_openai.chat.completions.create.side_effect = [
            make_response("not json"),
            make_response(json.dumps({"accurate": True})),
        ]

        client = LLMClient(model=config.MODEL_NAME, prompt_path=self.prompt_path)
        result = client.audit_pair(
            query="kodak photo paper",
            product_title="Kodak glossy paper",
            product_description="Photo paper",
            product_bullet_point="8.5 x 11",
        )

        self.assertEqual(result, {"accurate": True, "reformulated_query": None})
        self.assertEqual(self.mock_openai.chat.completions.create.call_count, 2)

    def test_raises_after_retry(self) -> None:
        self.mock_openai.chat.completions.create.side_effect = [
            make_response("{}"),
            make_response("still not json"),
        ]

        client = LLMClient(model=config.MODEL_NAME, prompt_path=self.prompt_path)

        with self.assertRaisesRegex(
            ValueError,
            "Unparseable LLM response after 2 attempts: still not json",
        ):
            client.audit_pair(
                query="dewalt screwdriver",
                product_title="Dewalt kit",
                product_description="Cordless screwdriver",
                product_bullet_point="8v max",
            )

        self.assertEqual(self.mock_openai.chat.completions.create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
