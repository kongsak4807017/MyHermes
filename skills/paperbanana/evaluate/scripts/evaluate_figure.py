#!/usr/bin/env python3
"""
PaperBanana Figure Evaluator — VLM-as-Judge evaluation for academic figures.
Evaluates generated diagrams across 4 dimensions: faithfulness, readability, conciseness, aesthetics.
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Add shared scripts to path
SHARED_SCRIPTS = Path(__file__).parent.parent.parent / "shared-scripts"
if SHARED_SCRIPTS.exists():
    sys.path.insert(0, str(SHARED_SCRIPTS))

from paperbanana_utils import call_llm, load_env_file, save_metadata


@dataclass
class EvaluateConfig:
    vlm_provider: str = "openai"
    vlm_model: str = "gpt-4o"
    verbose: bool = False
    output_dir: str = "outputs"


class FigureEvaluator:
    """Evaluates academic figures using VLM-as-Judge."""

    def __init__(self, config: Optional[EvaluateConfig] = None, **kwargs):
        self.config = config or EvaluateConfig(**kwargs)

    async def evaluate(
        self,
        generated_path: str,
        context: str,
        caption: str,
        reference_path: Optional[str] = None,
    ) -> dict:
        """Run full evaluation on a generated figure."""
        start_time = time.time()
        run_id = f"eval_{time.strftime('%Y%m%d_%H%M%S')}"

        mode = "comparative" if reference_path else "standalone"

        # Build evaluation prompt
        evaluator_prompt = self._load_prompt("evaluator")

        # Prepare image descriptions
        generated_desc = self._describe_image(generated_path)
        reference_desc = None
        if reference_path:
            reference_desc = self._describe_image(reference_path)

        user_content = self._build_evaluation_input(
            generated_desc=generated_desc,
            reference_desc=reference_desc,
            context=context,
            caption=caption,
            mode=mode,
        )

        print(f"[Evaluate] Running {mode} evaluation...")
        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": evaluator_prompt},
                {"role": "user", "content": user_content},
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        # Validate and normalize response
        result = self._normalize_result(response, mode)

        elapsed = time.time() - start_time
        result["elapsed_seconds"] = elapsed
        result["run_id"] = run_id
        result["generated_path"] = generated_path
        result["reference_path"] = reference_path

        return result

    def _describe_image(self, image_path: str) -> str:
        """Generate a text description of an image for evaluation."""
        path = Path(image_path)
        if not path.exists():
            return f"[Image not found: {image_path}]"

        # For vision-capable models, we could send the image directly
        # For now, return file info as placeholder
        size = path.stat().st_size
        return f"Image file: {path.name} ({size} bytes) at {image_path}"

    def _build_evaluation_input(
        self,
        generated_desc: str,
        reference_desc: Optional[str],
        context: str,
        caption: str,
        mode: str,
    ) -> str:
        """Build the evaluation input text."""
        lines = [
            f"Evaluation Mode: {mode}",
            "",
            f"Figure Caption: {caption}",
            "",
            "Source Context:",
            context,
            "",
            f"Generated Image: {generated_desc}",
        ]

        if reference_desc:
            lines.extend([
                "",
                f"Reference Image: {reference_desc}",
            ])

        return "\n".join(lines)

    def _load_prompt(self, name: str) -> str:
        prompt_path = (
            Path(__file__).parent.parent.parent
            / "shared-references"
            / "references"
            / "prompts"
            / f"{name}.md"
        )
        if prompt_path.exists():
            return prompt_path.read_text()
        return f"# {name.replace('-', ' ').title()} Prompt\nEvaluate the figure and produce structured output."

    def _normalize_result(self, response: Any, mode: str) -> dict:
        """Ensure result has all required fields."""
        if not isinstance(response, dict):
            response = {"raw_response": str(response)}

        # Ensure dimension structure
        for dim in ["faithfulness", "readability", "conciseness", "aesthetics"]:
            if dim not in response:
                response[dim] = {"score": 5.0, "rationale": "Not evaluated", "findings": []}

        # Calculate aggregate if missing
        if "aggregate_score" not in response:
            scores = [
                response.get("faithfulness", {}).get("score", 5),
                response.get("readability", {}).get("score", 5),
                response.get("conciseness", {}).get("score", 5),
                response.get("aesthetics", {}).get("score", 5),
            ]
            response["aggregate_score"] = sum(scores) / len(scores)

        # Determine verdict if missing
        if "verdict" not in response:
            primary = [response.get("faithfulness", {}).get("score", 5), response.get("readability", {}).get("score", 5)]
            agg = response["aggregate_score"]

            if agg >= 8.0 and all(p >= 7.0 for p in primary):
                response["verdict"] = "ACCEPT"
            elif agg >= 5.0 and all(p >= 4.0 for p in primary):
                response["verdict"] = "REVISE"
            else:
                response["verdict"] = "REJECT"

        response["evaluation_mode"] = mode
        return response

    async def evaluate_with_vision(
        self,
        generated_path: str,
        context: str,
        caption: str,
        reference_path: Optional[str] = None,
    ) -> dict:
        """Evaluate using vision-capable model with actual image input."""
        # This requires a vision-capable API
        # For OpenAI GPT-4o, we can send base64 images
        try:
            return await self._evaluate_with_vision_api(
                generated_path, context, caption, reference_path
            )
        except Exception as e:
            print(f"[Vision] Fallback to text-only evaluation: {e}")
            return await self.evaluate(generated_path, context, caption, reference_path)

    async def _evaluate_with_vision_api(
        self,
        generated_path: str,
        context: str,
        caption: str,
        reference_path: Optional[str] = None,
    ) -> dict:
        """Use vision API for evaluation."""
        evaluator_prompt = self._load_prompt("evaluator")

        # Build message with images
        content = [
            {"type": "text", "text": f"Evaluate this figure for a research paper. Caption: {caption}\n\nSource Context:\n{context}"},
        ]

        # Add generated image
        generated_b64 = self._image_to_base64(generated_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{generated_b64}"},
        })

        if reference_path:
            reference_b64 = self._image_to_base64(reference_path)
            content.append({"type": "text", "text": "Reference image (human-created):"})
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{reference_b64}"},
            })

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": evaluator_prompt},
                {"role": "user", "content": content},
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        return self._normalize_result(response, "comparative" if reference_path else "standalone")

    def _image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


async def main():
    parser = argparse.ArgumentParser(description="Evaluate academic figures")
    parser.add_argument("--generated", "-g", required=True, help="Path to generated image")
    parser.add_argument("--reference", "-r", help="Path to human reference image")
    parser.add_argument("--context", required=True, help="Path to source context text file")
    parser.add_argument("--caption", "-c", required=True, help="Figure caption")
    parser.add_argument("--vlm-provider", default="openai", choices=["openai", "gemini", "openrouter"])
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--vision", action="store_true", help="Use vision-capable model")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    load_env_file(Path.home() / ".paperbanana" / ".env")

    if not Path(args.generated).exists():
        print(f"Error: Generated image not found: {args.generated}")
        sys.exit(1)

    context_text = Path(args.context).read_text()

    config = EvaluateConfig(
        vlm_provider=args.vlm_provider,
        verbose=args.verbose,
    )

    evaluator = FigureEvaluator(config)

    if args.vision:
        result = await evaluator.evaluate_with_vision(
            generated_path=args.generated,
            context=context_text,
            caption=args.caption,
            reference_path=args.reference,
        )
    else:
        result = await evaluator.evaluate(
            generated_path=args.generated,
            context=context_text,
            caption=args.caption,
            reference_path=args.reference,
        )

    # Save or print results
    if args.output:
        save_metadata(result, args.output)
        print(f"[✓] Evaluation saved to: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Summary
    print(f"\n=== Evaluation Summary ===")
    print(f"Mode: {result['evaluation_mode']}")
    print(f"Aggregate Score: {result['aggregate_score']:.2f}/10")
    print(f"Verdict: {result['verdict']}")
    print(f"Faithfulness: {result.get('faithfulness', {}).get('score', 'N/A')}")
    print(f"Readability: {result.get('readability', {}).get('score', 'N/A')}")
    print(f"Conciseness: {result.get('conciseness', {}).get('score', 'N/A')}")
    print(f"Aesthetics: {result.get('aesthetics', {}).get('score', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
