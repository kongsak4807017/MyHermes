---
name: prompt-testing
description: "Prompt testing, red-teaming, and evaluation for LLM agents using Promptfoo, DeepEval, and RAGAS patterns."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [promptfoo, deepeval, ragas]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Prompt Testing, Red Teaming, Evaluation, Promptfoo, DeepEval, RAGAS, LLM Testing, Benchmark]
---

# Prompt Testing & Red-Teaming

## What's inside

Comprehensive prompt testing and evaluation: unit tests for prompts, red-teaming attacks, RAG evaluation, and regression testing.

## Quick start

**Install Promptfoo**:
```bash
npm install -g promptfoo
```

**Run a test**:
```bash
promptfoo eval -c promptfooconfig.yaml
```

**Example config**:
```yaml
# promptfooconfig.yaml
prompts:
  - "Translate {{text}} to {{language}}"
  - "Convert this to {{language}}: {{text}}"

providers:
  - openai:gpt-4
  - anthropic:claude-3-opus

tests:
  - vars:
      text: "Hello world"
      language: "French"
    assert:
      - type: contains
        value: "Bonjour"
  - vars:
      text: "How are you?"
      language: "Spanish"
    assert:
      - type: contains
        value: "cómo estás"
```

## Common workflows

### Workflow 1: Prompt Regression Testing

```bash
# Create test suite
cat > prompt_tests.yaml << 'EOF'
prompts:
  - file://prompts/summarize.txt
  - file://prompts/summarize_v2.txt

providers:
  - openai:gpt-4

tests:
  - description: "Basic summary"
    vars:
      article: "The quick brown fox jumps over the lazy dog."
    assert:
      - type: contains
        value: "fox"
      - type: contains
        value: "dog"
      - type: length
        max: 50
EOF

# Run tests
promptfoo eval -c prompt_tests.yaml

# View results
promptfoo view
```

### Workflow 2: Red-Teaming

```bash
# Red-team config
cat > redteam.yaml << 'EOF'
targets:
  - id: openai:gpt-4
    config:
      temperature: 0.5

plugins:
  - harmful
  - pii
  - jailbreak
  - hallucination

strategies:
  - basic
  - multilingual
  - prompt-injection
EOF

# Run red-team
promptfoo redteam eval -c redteam.yaml
```

### Workflow 3: RAG Evaluation with RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset

# Prepare data
data = Dataset.from_dict({
    "question": ["What is Python?"],
    "answer": ["Python is a programming language."],
    "contexts": [["Python is a high-level programming language."]],
    "ground_truth": ["Python is a programming language."]
})

# Evaluate
results = evaluate(
    data,
    metrics=[faithfulness, answer_relevancy, context_precision]
)

print(results)
```

### Workflow 4: DeepEval Custom Metrics

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

# Define test
test_case = LLMTestCase(
    input="What is Python?",
    actual_output="Python is a programming language.",
    retrieval_context=["Python is a high-level programming language."]
)

# Evaluate
relevancy = AnswerRelevancyMetric(threshold=0.7)
faithfulness = FaithfulnessMetric(threshold=0.7)

assert_test(test_case, [relevancy, faithfulness])
```

## Test Types

| Type | Tool | Use Case |
|------|------|----------|
| Prompt regression | Promptfoo | Ensure prompts don't degrade |
| Red-teaming | Promptfoo | Find safety vulnerabilities |
| RAG evaluation | RAGAS | Evaluate retrieval quality |
| Custom metrics | DeepEval | Domain-specific evaluation |
| A/B testing | Promptfoo | Compare prompt versions |

## Common issues

**Issue: Tests flaky**
- Set temperature=0
- Use deterministic providers
- Add retry logic

**Issue: Red-team too slow**
- Reduce plugin count
- Use parallel execution
- Focus on high-risk plugins

## Resources

- Promptfoo: https://promptfoo.dev
- DeepEval: https://deepeval.com
- RAGAS: https://ragas.io
