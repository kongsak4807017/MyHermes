#!/usr/bin/env python3
"""
PaperBanana Plot Generator — Multi-agent statistical plot generation from data.
Reimplements PaperBanana's plot generation using Hermes native tools.
"""

import argparse
import asyncio
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

from paperbanana_utils import (
    call_llm,
    generate_image,
    load_env_file,
    save_metadata,
    sniff_data_schema,
)


@dataclass
class PlotConfig:
    vlm_provider: str = "openai"
    vlm_model: str = "gpt-4o"
    image_provider: str = "openai"
    image_model: str = "dall-e-3"
    venue: str = "neurips"
    aspect_ratio: str = "4:3"
    iterations: int = 3
    output_format: str = "png"
    verbose: bool = False
    output_dir: str = "outputs"


class DataAnalyzer:
    """Analyze data schema and generate descriptive summary."""

    def __init__(self, config: PlotConfig):
        self.config = config

    async def analyze(self, data_path: str) -> dict:
        """Analyze data file and return schema + summary."""
        schema = sniff_data_schema(data_path)
        if "error" in schema:
            return schema

        # Generate natural language summary
        summary_prompt = f"""Analyze this data schema and provide a concise summary:

{json.dumps(schema, indent=2, ensure_ascii=False)}

Provide:
1. What the data represents
2. Key columns and their roles
3. Suggested plot types
4. Any notable patterns or considerations
"""

        summary = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": "You are a data analysis expert."},
                {"role": "user", "content": summary_prompt},
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        return {
            "schema": schema,
            "summary": summary,
        }


class PlotPlanner:
    """Generate detailed plot plan from data analysis and intent."""

    def __init__(self, config: PlotConfig):
        self.config = config

    async def plan(self, data_analysis: dict, intent: str) -> dict:
        """Generate structured plot plan."""
        planner_prompt = self._load_prompt("plot-planner")

        context = {
            "data_schema": data_analysis["schema"],
            "data_summary": data_analysis["summary"],
            "intent": intent,
            "venue": self.config.venue,
            "aspect_ratio": self.config.aspect_ratio,
        }

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": planner_prompt},
                {
                    "role": "user",
                    "content": f"Context:\n{json.dumps(context, indent=2, ensure_ascii=False)}",
                },
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        if isinstance(response, dict):
            return response
        return {"raw_plan": response}

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


class PlotVisualizer:
    """Render plot plan into an image or matplotlib code."""

    def __init__(self, config: PlotConfig):
        self.config = config

    async def visualize(self, plot_plan: dict, data_path: str, iteration: int = 0) -> dict:
        """Generate plot image from plan."""
        # First, generate matplotlib code
        code = await self._generate_matplotlib_code(plot_plan, data_path)

        # Try to execute the code to generate the plot
        image_path = await self._execute_plot_code(code, data_path)

        if image_path:
            return {
                "code": code,
                "image_path": image_path,
                "method": "matplotlib",
            }

        # Fallback: generate via image_gen API
        visualizer_prompt = self._load_prompt("visualizer")
        plot_description = json.dumps(plot_plan, indent=2, ensure_ascii=False)

        response = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": visualizer_prompt},
                {
                    "role": "user",
                    "content": f"Plot Plan:\n{plot_description}\n\nFormat: {self.config.output_format}",
                },
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        main_prompt = self._extract_main_prompt(response)
        image_result = await generate_image(
            provider=self.config.image_provider,
            model=self.config.image_model,
            prompt=main_prompt,
            size="1024x1024",
            verbose=self.config.verbose,
        )

        return {
            "prompt": main_prompt,
            "image_path": image_result.get("path"),
            "image_url": image_result.get("url"),
            "code": code,
            "method": "image_gen",
        }

    async def _generate_matplotlib_code(self, plot_plan: dict, data_path: str) -> str:
        """Generate matplotlib Python code from plot plan."""
        code_prompt = f"""Generate complete, runnable Python code using matplotlib to create this plot:

Plot Plan:
{json.dumps(plot_plan, indent=2, ensure_ascii=False)}

Data file path: {data_path}

Requirements:
1. Use matplotlib and pandas
2. Read data from the file path
3. Follow the plot plan exactly
4. Use venue-appropriate styling
5. Save to a file using plt.savefig()
6. Do NOT show the plot (no plt.show())
7. Include proper labels, title, legend
8. Use colors appropriate for {self.config.venue}

Return ONLY the Python code, no markdown formatting.
"""

        code = await call_llm(
            provider=self.config.vlm_provider,
            model=self.config.vlm_model,
            messages=[
                {"role": "system", "content": "You are an expert data visualization programmer."},
                {"role": "user", "content": code_prompt},
            ],
            json_mode=False,
            verbose=self.config.verbose,
        )

        # Clean up code block markers
        code = code.replace("```python", "").replace("```", "").strip()
        return code

    async def _execute_plot_code(self, code: str, data_path: str) -> Optional[str]:
        """Execute matplotlib code and return image path."""
        try:
            import matplotlib
            matplotlib.use("Agg")  # Non-interactive backend

            # Create temporary file for the image
            temp_path = Path(tempfile.gettempdir()) / f"paperbanana_plot_{os.urandom(4).hex()}.png"

            # Modify code to save to our path
            if "plt.savefig" not in code:
                code += f"\nplt.savefig('{temp_path}', dpi=300, bbox_inches='tight')"
            else:
                code = code.replace("plt.savefig(", f"plt.savefig('{temp_path}', dpi=300, bbox_inches='tight')\n# plt.savefig(")

            # Execute in isolated namespace
            namespace = {
                "__name__": "__main__",
                "data_path": data_path,
            }
            exec(code, namespace)

            if temp_path.exists():
                return str(temp_path)
        except Exception as e:
            if self.config.verbose:
                print(f"[Plot] Matplotlib execution failed: {e}")

        return None

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
        match = __import__("re").search(r"## Main Prompt\n+(.+?)(?=\n## |\Z)", response, __import__("re").DOTALL)
        if match:
            return match.group(1).strip()
        return response.strip()


class PlotCritic:
    """Evaluate generated plot against data and intent."""

    def __init__(self, config: PlotConfig):
        self.config = config

    async def evaluate(self, image_description: str, plot_plan: dict, intent: str, iteration: int) -> dict:
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
                        f"Plot Plan:\n{json.dumps(plot_plan, indent=2, ensure_ascii=False)}\n\n"
                        f"Communicative Intent: {intent}\n\n"
                        f"Generated Plot Description:\n{image_description}"
                    ),
                },
            ],
            json_mode=True,
            verbose=self.config.verbose,
        )

        if isinstance(response, dict):
            response.setdefault("iteration", iteration)
            response.setdefault("verdict", "NEEDS_REVISION")
            response.setdefault("satisfied", False)
            return response

        return {
            "iteration": iteration,
            "verdict": "NEEDS_REVISION",
            "satisfied": False,
            "revised_description": str(response),
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


class PlotPipeline:
    """Orchestrates the full plot generation pipeline."""

    def __init__(self, config: Optional[PlotConfig] = None, **kwargs):
        self.config = config or PlotConfig(**kwargs)
        self.analyzer = DataAnalyzer(self.config)
        self.planner = PlotPlanner(self.config)
        self.visualizer = PlotVisualizer(self.config)
        self.critic = PlotCritic(self.config)

    async def generate(
        self,
        data_path: str,
        intent: str,
        output_path: Optional[str] = None,
    ) -> dict:
        """Run the full plot generation pipeline."""
        start_time = time.time()
        run_id = f"plot_{time.strftime('%Y%m%d_%H%M%S')}"

        if output_path is None:
            output_dir = Path(self.config.output_dir) / run_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / f"plot.{self.config.output_format}")
        else:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "run_id": run_id,
            "config": self.config.__dict__,
            "intent": intent,
            "data_path": data_path,
            "phases": [],
        }

        # Phase 1: Data Analysis
        print("[Phase 1] Analyzing data...")
        data_analysis = await self.analyzer.analyze(data_path)
        metadata["phases"].append({"phase": "analysis", "result": data_analysis})

        # Phase 2: Planning
        print("[Phase 2] Planning plot...")
        plot_plan = await self.planner.plan(data_analysis, intent)
        metadata["phases"].append({"phase": "planning", "plan": plot_plan})

        # Phase 3: Visualization + Critic (iterative)
        current_plan = plot_plan
        for iteration in range(1, self.config.iterations + 1):
            print(f"[Phase 3a] Visualization iteration {iteration}...")
            viz_result = await self.visualizer.visualize(current_plan, data_path, iteration)
            metadata["phases"].append({
                "phase": f"visualization_{iteration}",
                "result": viz_result,
            })

            print(f"[Phase 3b] Critic evaluation iteration {iteration}...")
            critique = await self.critic.evaluate(
                image_description=viz_result.get("prompt", viz_result.get("code", "")),
                plot_plan=current_plan,
                intent=intent,
                iteration=iteration,
            )
            metadata["phases"].append({
                "phase": f"critique_{iteration}",
                "critique": critique,
            })

            if critique.get("satisfied", False):
                print(f"[✓] Critic satisfied at iteration {iteration}")
                break

            if iteration < self.config.iterations:
                current_plan = critique.get("revised_description", current_plan)
                print(f"[→] Applying revisions for iteration {iteration + 1}")

        # Save final output
        final_image = viz_result.get("image_path")
        if final_image and Path(final_image).exists():
            import shutil
            shutil.copy(final_image, output_path)
        elif final_image:
            output_path = final_image

        elapsed = time.time() - start_time
        metadata["elapsed_seconds"] = elapsed
        metadata["final_output"] = output_path

        meta_path = output_dir / "metadata.json"
        save_metadata(metadata, str(meta_path))

        print(f"[✓] Plot saved to: {output_path}")
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
    parser = argparse.ArgumentParser(description="Generate statistical plots from data")
    parser.add_argument("--data", "-d", required=True, help="Path to CSV or JSON file")
    parser.add_argument("--intent", required=True, help="Communicative intent for the plot")
    parser.add_argument("--output", "-o", help="Output image path")
    parser.add_argument("--venue", default="neurips", choices=["neurips", "icml", "acl", "ieee", "arxiv"])
    parser.add_argument("--aspect-ratio", "-ar", default="4:3", choices=["16:9", "4:3", "1:1", "3:2"])
    parser.add_argument("--vlm-provider", default="openai", choices=["openai", "gemini", "openrouter"])
    parser.add_argument("--iterations", "-n", type=int, default=3)
    parser.add_argument("--format", "-f", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--output-dir", default="outputs")

    args = parser.parse_args()

    load_env_file(Path.home() / ".paperbanana" / ".env")

    if not Path(args.data).exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    config = PlotConfig(
        vlm_provider=args.vlm_provider,
        venue=args.venue,
        aspect_ratio=args.aspect_ratio,
        iterations=args.iterations,
        output_format=args.format,
        verbose=args.verbose,
        output_dir=args.output_dir,
    )

    pipeline = PlotPipeline(config)
    result = await pipeline.generate(
        data_path=args.data,
        intent=args.intent,
        output_path=args.output,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
