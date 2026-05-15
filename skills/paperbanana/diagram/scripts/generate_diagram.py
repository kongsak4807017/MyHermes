#!/usr/bin/env python3
"""
PaperBanana Diagram Generator — Multi-agent academic diagram generation pipeline.
Reimplements PaperBanana's methodology diagram generation using Hermes native tools.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Add shared scripts to path
SHARED_SCRIPTS = Path(__file__).parent.parent.parent / "shared-scripts"
if SHARED_SCRIPTS.exists():
    sys.path.insert(0, str(SHARED_SCRIPTS))

from paperbanana_utils import (
    call_llm,
    generate_image,
    load_env_file,
    parse_pdf_text,
    save_metadata,
    setup_logging,
)


@dataclass
class DiagramConfig:
    vlm_provider: str = "openai"
    vlm_model: str = "gpt-4o"
    image_provider: str = "openai"
    image_model: str = "dall-e-3"
    venue: str = "neurips"
    optimize: bool = False
    auto_refine: bool = False
    max_iterations: int = 30
    iterations: int = 3
    output_format: str = "png"
    verbose: bool = False
    output_dir: str = "outputs"


class InputOptimizer:
    """Phase 0: Parallel context enrichment and caption sharpening."""

    def __init__(self, config: DiagramConfig):
        self.config = config

    async def optimize(self, source_context: str, caption: str) -> dict:
        """Run context enricher and caption sharpener in parallel."""
        enricher_prompt = self._load_prompt("context-enricher")
        sharpener_prompt = self._load_prompt("caption-sharpener")

        enrich_task = call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": enricher_prompt},
                {"role": "user", "content": f"Methodology text:\n{source_context}"},
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        sharpen_task = call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": sharpener_prompt},
                {"role": "user", "content": f"Caption: {caption}"},
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        enriched, sharpened = await asyncio.gather(enrich_task, sharpen_task)

        return {
            "structured_context": enriched,
            "sharpened_caption": sharpened,
        }

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
        return f"# {name.replace('-', ' ').title()} Prompt\nProcess the input and produce structured output."


class Planner:
    """Phase 1: Generate detailed diagram plan from structured context."""

    def __init__(self, config: DiagramConfig):
        self.config = config

    async def plan(self, structured_context: dict, sharpened_caption: dict) -> str:
        planner_prompt = self._load_prompt("planner")

        context_json = json.dumps(structured_context, indent=2, ensure_ascii=False)
        caption_json = json.dumps(sharpened_caption, indent=2, ensure_ascii=False)

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": planner_prompt},
                {
                    "role": "user",
                    "content": f"Structured Context:\n{context_json}\n\nSharpened Caption:\n{caption_json}",
                },
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        return response

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
        return f"# {name.replace('-', ' ').title()} Prompt\nProcess the input and produce structured output."


class Stylist:
    """Apply venue-specific aesthetic guidelines."""

    def __init__(self, config: DiagramConfig):
        self.config = config

    async def style(self, diagram_plan: str) -> str:
        stylist_prompt = self._load_prompt("stylist")

        # Inject venue-specific guidelines
        venue_guidelines = self._load_venue_checklist()

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": stylist_prompt},
                {
                    "role": "user",
                    "content": f"Venue: {self.config.venue}\n\nVenue Guidelines:\n{venue_guidelines}\n\nDiagram Plan:\n{diagram_plan}",
                },
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        return response

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
        return f"# {name.replace('-', ' ').title()} Prompt\nProcess the input and produce structured output."

    def _load_venue_checklist(self) -> str:
        checklist_path = (
            Path(__file__).parent.parent.parent
            / "shared-references"
            / "references"
            / "venue-checklists.md"
        )
        if checklist_path.exists():
            return checklist_path.read_text()
        return "# Venue Guidelines\nUse professional academic styling."


class Visualizer:
    """Render styled specification into an image."""

    def __init__(self, config: DiagramConfig):
        self.config = config

    async def visualize(self, styled_spec: str, iteration: int = 0) -> dict:
        visualizer_prompt = self._load_prompt("visualizer")

        # Generate the image generation prompt
        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": visualizer_prompt},
                {
                    "role": "user",
                    "content": f"Styled Specification:\n{styled_spec}\n\nFormat: {self.config.output_format}\nIteration: {iteration}",
                },
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        # Extract the main prompt from the response
        main_prompt = self._extract_main_prompt(response)

        # Generate image using the configured provider
        image_result = await generate_image(
            provider=self.config.image_provider,
            model=self.config.image_model,
            prompt=main_prompt,
            size="1024x1024",
            quality="standard",
            verbose=self.config.verbose,
        )

        return {
            "prompt": main_prompt,
            "image_path": image_result.get("path"),
            "image_url": image_result.get("url"),
            "raw_response": response,
        }

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
        return f"# {name.replace('-', ' ').title()} Prompt\nProcess the input and produce structured output."

    def _extract_main_prompt(self, response: str) -> str:
        """Extract the main prompt from visualizer output."""
        # Try to find "## Main Prompt" section
        match = re.search(r"## Main Prompt\n+(.+?)(?=\n## |\Z)", response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: use the whole response
        return response.strip()


class Critic:
    """Evaluate generated diagram and provide revision feedback."""

    def __init__(self, config: DiagramConfig):
        self.config = config

    async def evaluate(
        self,
        image_description: str,
        source_context: str,
        caption: str,
        iteration: int,
    ) -> dict:
        critic_prompt = self._load_prompt("critic")

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": critic_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Iteration: {iteration}\n\n"
                        f"Generated Image Description:\n{image_description}\n\n"
                        f"Source Context:\n{source_context}\n\n"
                        f"Caption: {caption}"
                    ),
                },
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        # Ensure required fields exist
        if isinstance(response, dict):
            response.setdefault("iteration", iteration)
            response.setdefault("verdict", "NEEDS_REVISION")
            response.setdefault("satisfied", False)
            response.setdefault("revised_description", "")
        else:
            response = {
                "iteration": iteration,
                "verdict": "NEEDS_REVISION",
                "satisfied": False,
                "revised_description": str(response),
                "error": "Expected JSON response",
            }

        return response

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
        return f"# {name.replace('-', ' ').title()} Prompt\nProcess the input and produce structured output."


class DiagramPipeline:
    """Orchestrates the full multi-agent diagram generation pipeline."""

    def __init__(self, config: Optional[DiagramConfig] = None, **kwargs):
        self.config = config or DiagramConfig(**kwargs)
        self.optimizer = InputOptimizer(self.config)
        self.planner = Planner(self.config)
        self.stylist = Stylist(self.config)
        self.visualizer = Visualizer(self.config)
        self.critic = Critic(self.config)

    async def generate(
        self,
        source_context: str,
        caption: str,
        output_path: Optional[str] = None,
    ) -> dict:
        """Run the full generation pipeline."""
        start_time = time.time()
        run_id = f"run_{time.strftime('%Y%m%d_%H%M%S')}"

        if output_path is None:
            output_dir = Path(self.config.output_dir) / run_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / f"final_output.{self.config.output_format}")
        else:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "run_id": run_id,
            "config": self.config.__dict__,
            "caption": caption,
            "phases": [],
        }

        # Phase 0: Input Optimization (optional)
        if self.config.optimize:
            print("[Phase 0] Optimizing inputs...")
            optimized = await self.optimizer.optimize(source_context, caption)
            structured_context = optimized["structured_context"]
            sharpened_caption = optimized["sharpened_caption"]
            metadata["phases"].append({
                "phase": "optimization",
                "structured_context": structured_context,
                "sharpened_caption": sharpened_caption,
            })
        else:
            structured_context = {"raw": source_context}
            sharpened_caption = {"original": caption}

        # Phase 1: Planning
        print("[Phase 1] Planning diagram...")
        diagram_plan = await self.planner.plan(structured_context, sharpened_caption)
        metadata["phases"].append({"phase": "planning", "plan": diagram_plan})

        # Phase 2a: Styling
        print("[Phase 2a] Applying venue style...")
        styled_spec = await self.stylist.style(diagram_plan)
        metadata["phases"].append({"phase": "styling", "styled_spec": styled_spec})

        # Phase 2b-c: Visualization + Critic (iterative)
        current_spec = styled_spec
        max_iter = self.config.max_iterations if self.config.auto_refine else self.config.iterations

        for iteration in range(1, max_iter + 1):
            print(f"[Phase 2b] Visualization iteration {iteration}...")
            viz_result = await self.visualizer.visualize(current_spec, iteration)
            metadata["phases"].append({
                "phase": f"visualization_{iteration}",
                "result": viz_result,
            })

            print(f"[Phase 2c] Critic evaluation iteration {iteration}...")
            critique = await self.critic.evaluate(
                image_description=viz_result["prompt"],
                source_context=source_context,
                caption=caption,
                iteration=iteration,
            )
            metadata["phases"].append({
                "phase": f"critique_{iteration}",
                "critique": critique,
            })

            if critique.get("satisfied", False):
                print(f"[✓] Critic satisfied at iteration {iteration}")
                break

            if iteration < max_iter:
                current_spec = critique.get("revised_description", current_spec)
                print(f"[→] Applying revisions for iteration {iteration + 1}")

        # Save final output
        final_image = viz_result.get("image_path") or viz_result.get("image_url")
        if final_image and Path(final_image).exists():
            import shutil
            shutil.copy(final_image, output_path)
        elif viz_result.get("image_path"):
            output_path = viz_result["image_path"]

        elapsed = time.time() - start_time
        metadata["elapsed_seconds"] = elapsed
        metadata["final_output"] = output_path

        # Save metadata
        meta_path = output_dir / "metadata.json"
        save_metadata(metadata, str(meta_path))

        print(f"[✓] Diagram saved to: {output_path}")
        print(f"[✓] Metadata saved to: {meta_path}")
        print(f"[✓] Elapsed: {elapsed:.1f}s")

        return {
            "image_path": output_path,
            "metadata_path": str(meta_path),
            "run_id": run_id,
            "elapsed_seconds": elapsed,
            "iterations": iteration,
        }


async def main():
    parser = argparse.ArgumentParser(description="Generate academic methodology diagrams")
    parser.add_argument("--input", "-i", required=True, help="Input text file or PDF")
    parser.add_argument("--caption", "-c", required=True, help="Figure caption")
    parser.add_argument("--output", "-o", help="Output image path")
    parser.add_argument("--iterations", "-n", type=int, default=3, help="Refinement iterations")
    parser.add_argument("--auto", action="store_true", help="Auto-refine until satisfied")
    parser.add_argument("--max-iterations", type=int, default=30, help="Max iterations for auto")
    parser.add_argument("--optimize", action="store_true", help="Enable input optimization")
    parser.add_argument("--venue", default="neurips", choices=["neurips", "icml", "acl", "ieee", "arxiv"])
    parser.add_argument("--vlm-provider", default="openai", choices=["openai", "gemini", "openrouter"])
    parser.add_argument("--image-provider", default="openai", choices=["openai", "gemini", "openrouter"])
    parser.add_argument("--format", "-f", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--pdf-pages", help="PDF page selection (e.g., '1-5', '2,4,6-8')")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--output-dir", default="outputs")

    args = parser.parse_args()

    # Load environment
    load_env_file(Path.home() / ".paperbanana" / ".env")

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if input_path.suffix.lower() == ".pdf":
        source_context = parse_pdf_text(str(input_path), args.pdf_pages)
    else:
        source_context = input_path.read_text()

    # Create config
    config = DiagramConfig(
        vlm_provider=args.vlm_provider,
        image_provider=args.image_provider,
        venue=args.venue,
        optimize=args.optimize,
        auto_refine=args.auto,
        max_iterations=args.max_iterations,
        iterations=args.iterations,
        output_format=args.format,
        verbose=args.verbose,
        output_dir=args.output_dir,
    )

    pipeline = DiagramPipeline(config)
    result = await pipeline.generate(
        source_context=source_context,
        caption=args.caption,
        output_path=args.output,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
