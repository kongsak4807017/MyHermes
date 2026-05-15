---
name: vercel-ai-agents
description: "AI agent patterns from Vercel Labs: coding agents, research agents, workflow builders, and multi-agent systems."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [nextjs, typescript, ai-sdk]
metadata:
  hermes:
    tags: [AI Agents, Multi-Agent, Coding Agents, Research Agents, Vercel, Next.js]
---

# Vercel AI Agents

Patterns for building AI agents from vercel-labs repositories: coding agents, research agents, workflow builders, and multi-agent systems.

## When to use

**Use when building:**
- Multi-agent coding platforms
- Deep research agents
- AI workflow canvases
- Lead generation agents
- Data analysis agents
- Sandbox-based code execution agents

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                          │
│              ┌─────────────┐  ┌─────────────┐             │
│              │   Planner    │  │  Executor   │             │
│              │  (Reasoning)   │  │  (Tools)    │             │
│              └──────┬──────┘  └──────┬──────┘             │
│                     │                │                     │
│              ┌──────▼────────────────▼──────┐             │
│              │      Sandbox / Vercel         │             │
│              │      Secure Execution         │             │
│              └─────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
npm install ai @ai-sdk/openai @vercel/sandbox
```

## Patterns

### Pattern 1: Coding Agent with Sandbox

From `coding-agent-template`:

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const codingAgent = {
  async execute(prompt: string) {
    const result = await generateText({
      model: openai('gpt-4o'),
      system: `You are a coding agent. Use the sandbox to execute code.
Available tools:
- write_file: Write code to sandbox
- read_file: Read file from sandbox
- execute_command: Run command in sandbox
- search_code: Search code in sandbox`,
      tools: {
        write_file: tool({
          description: 'Write a file in the sandbox',
          parameters: z.object({
            path: z.string(),
            content: z.string(),
          }),
          execute: async ({ path, content }) => {
            await sandbox.fs.writeFile(path, content);
            return { success: true };
          },
        }),
        read_file: tool({
          description: 'Read a file from the sandbox',
          parameters: z.object({ path: z.string() }),
          execute: async ({ path }) => {
            const content = await sandbox.fs.readFile(path, 'utf-8');
            return { content };
          },
        }),
        execute_command: tool({
          description: 'Execute a command in the sandbox',
          parameters: z.object({ command: z.string() }),
          execute: async ({ command }) => {
            const result = await sandbox.shell.execute(command);
            return { stdout: result.stdout, stderr: result.stderr };
          },
        }),
        search_code: tool({
          description: 'Search code in the sandbox',
          parameters: z.object({ query: z.string() }),
          execute: async ({ query }) => {
            const results = await sandbox.search.search(query);
            return { results };
          },
        }),
      },
      maxSteps: 10,
      prompt,
    });

    return result;
  },
};
```

### Pattern 2: Development Timeline Agent

From `dev3000`:

```typescript
// Captures web app development timeline
import { generateText } from 'ai';

export async function captureDevTimeline(projectPath: string) {
  // 1. Analyze git history
  const commits = await analyzeGitHistory(projectPath);

  // 2. Generate timeline narrative
  const { text } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Analyze these commits and create a development timeline:
${JSON.stringify(commits)}`,
  });

  // 3. Generate visual timeline
  return {
    narrative: text,
    milestones: extractMilestones(commits),
    stats: calculateStats(commits),
  };
}
```

### Pattern 3: AI Workflow Canvas

From `tersa`:

```typescript
// Canvas-based AI workflow builder
interface WorkflowNode {
  id: string;
  type: 'agent' | 'tool' | 'condition' | 'output';
  config: Record<string, any>;
  connections: string[];
}

export async function executeWorkflow(nodes: WorkflowNode[], input: string) {
  const executed = new Set<string>();
  const results: Record<string, any> = {};

  async function executeNode(nodeId: string) {
    if (executed.has(nodeId)) return results[nodeId];

    const node = nodes.find(n => n.id === nodeId)!;

    // Execute dependencies first
    for (const depId of node.connections) {
      await executeNode(depId);
    }

    // Execute node
    const result = await executeNodeLogic(node, results);
    results[nodeId] = result;
    executed.add(nodeId);

    return result;
  }

  // Find start nodes (no incoming connections)
  const startNodes = nodes.filter(n =>
    !nodes.some(other => other.connections.includes(n.id))
  );

  for (const start of startNodes) {
    await executeNode(start.id);
  }

  return results;
}
```

### Pattern 4: Lead Generation Agent

From `lead-agent`:

```typescript
import { generateText, generateObject } from 'ai';
import { z } from 'zod';

const leadSchema = z.object({
  company: z.string(),
  contact: z.string(),
  email: z.string(),
  score: z.number(),
  insights: z.array(z.string()),
});

export async function researchLead(companyName: string) {
  // 1. Research company
  const research = await generateText({
    model: openai('gpt-4o'),
    tools: {
      search_web: tool({
        description: 'Search web for company info',
        parameters: z.object({ query: z.string() }),
        execute: async ({ query }) => searchWeb(query),
      }),
      analyze_website: tool({
        description: 'Analyze company website',
        parameters: z.object({ url: z.string() }),
        execute: async ({ url }) => scrapeWebsite(url),
      }),
    },
    maxSteps: 5,
    prompt: `Research ${companyName} as a sales lead`,
  });

  // 2. Score and structure lead
  const { object: lead } = await generateObject({
    model: openai('gpt-4o'),
    schema: leadSchema,
    prompt: `Based on this research, structure the lead: ${research.text}`,
  });

  return lead;
}
```

### Pattern 5: Data Analysis Agent

From `oss-data-analyst`:

```typescript
import { generateText } from 'ai';

export async function analyzeData(dataset: any[], question: string) {
  // 1. Generate analysis plan
  const { text: plan } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Create analysis plan for: ${question}
Dataset columns: ${Object.keys(dataset[0]).join(', ')}`,
  });

  // 2. Execute analysis steps
  const { text: analysis } = await generateText({
    model: openai('gpt-4o'),
    tools: {
      query_data: tool({
        description: 'Query dataset with SQL-like operations',
        parameters: z.object({ operation: z.string() }),
        execute: async ({ operation }) => executeDataOp(dataset, operation),
      }),
      visualize: tool({
        description: 'Create chart specification',
        parameters: z.object({ chartType: z.string(), config: z.string() }),
        execute: async ({ chartType, config }) => generateChartSpec(chartType, config),
      }),
    },
    maxSteps: 8,
    prompt: `Execute this plan: ${plan}`,
  });

  return { plan, analysis };
}
```

### Pattern 6: Deep Research Agent

From `deep-research-template`, `deep-research-server`:

```typescript
// Multi-step research with source tracking
interface ResearchResult {
  query: string;
  findings: Array<{
    claim: string;
    sources: string[];
    confidence: number;
  }>;
  gaps: string[];
  nextQueries: string[];
}

export async function deepResearch(topic: string, depth: number = 3) {
  const visited = new Set<string>();
  const findings: ResearchResult['findings'] = [];

  async function researchStep(query: string, currentDepth: number) {
    if (currentDepth <= 0 || visited.has(query)) return;
    visited.add(query);

    // Search and extract
    const { text } = await generateText({
      model: openai('gpt-4o'),
      tools: {
        search: tool({
          description: 'Search for information',
          parameters: z.object({ query: z.string() }),
          execute: async ({ query }) => webSearch(query),
        }),
        extract: tool({
          description: 'Extract structured info from URL',
          parameters: z.object({ url: z.string() }),
          execute: async ({ url }) => extractContent(url),
        }),
      },
      maxSteps: 5,
      prompt: `Research: ${query}. Find claims with sources.`,
    });

    // Parse findings
    const stepFindings = parseFindings(text);
    findings.push(...stepFindings);

    // Recursive research on gaps
    for (const gap of stepFindings.gaps || []) {
      await researchStep(gap, currentDepth - 1);
    }
  }

  await researchStep(topic, depth);

  return {
    topic,
    findings,
    summary: await synthesizeFindings(findings),
  };
}
```

### Pattern 7: x402 Payment Agent

From `x402-ai-starter`:

```typescript
// AI agent with micropayments
import { generateText } from 'ai';

export async function paidAgentService(userRequest: string, payment: Payment) {
  // Verify payment via x402
  const verified = await verifyPayment(payment);
  if (!verified) throw new Error('Payment required');

  // Execute agent task
  const result = await generateText({
    model: openai('gpt-4o'),
    prompt: userRequest,
  });

  // Charge based on usage
  await chargePayment(payment, calculateCost(result));

  return result;
}
```

### Pattern 8: Vectr - Natural Language Interface

From `vectr`:

```typescript
// Natural language to vector operations
import { generateObject } from 'ai';
import { z } from 'zod';

const vectorOpSchema = z.object({
  operation: z.enum(['search', 'insert', 'delete', 'update']),
  collection: z.string(),
  filter: z.record(z.any()).optional(),
  vector: z.array(z.number()).optional(),
  metadata: z.record(z.any()).optional(),
});

export async function naturalLanguageToVectorOp(query: string) {
  const { object } = await generateObject({
    model: openai('gpt-4o'),
    schema: vectorOpSchema,
    prompt: `Convert to vector DB operation: ${query}`,
  });

  return object;
}
```

### Pattern 9: Multi-Agent Orchestration

```typescript
// Agent swarm pattern
interface Agent {
  id: string;
  role: string;
  tools: string[];
  model: string;
}

export async function orchestrateAgents(agents: Agent[], task: string) {
  const results: Record<string, any> = {};

  // Parallel execution
  await Promise.all(
    agents.map(async (agent) => {
      const result = await generateText({
        model: openai(agent.model),
        system: `You are ${agent.role}. Use your assigned tools.`,
        tools: getToolsForAgent(agent.tools),
        prompt: task,
      });
      results[agent.id] = result;
    })
  );

  // Synthesize results
  const { text: synthesis } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Synthesize these agent outputs: ${JSON.stringify(results)}`,
  });

  return { individual: results, synthesis: synthesis.text };
}
```

### Pattern 10: Fact Checking Agent

From `ai-facts`:

```typescript
// Real-time fact checking
export async function factCheck(statement: string) {
  const { text } = await generateText({
    model: openai('gpt-4o'),
    tools: {
      search: tool({
        description: 'Search for fact verification',
        parameters: z.object({ query: z.string() }),
        execute: async ({ query }) => webSearch(query),
      }),
      verify: tool({
        description: 'Verify against knowledge base',
        parameters: z.object({ claim: z.string() }),
        execute: async ({ claim }) => checkKnowledgeBase(claim),
      }),
    },
    maxSteps: 5,
    prompt: `Fact check this statement: "${statement}". Provide sources and confidence score.`,
  });

  return parseFactCheckResult(text);
}
```

## Deployment

### Vercel Sandbox
```typescript
import { createSandbox } from '@vercel/sandbox';

const sandbox = await createSandbox({
  template: 'node',
  timeout: 300000, // 5 minutes
});
```

### Environment Variables
```
OPENAI_API_KEY=...
VERCEL_SANDBOX_TOKEN=...
X402_PAYMENT_KEY=...
```

## References

- https://github.com/vercel-labs/coding-agent-template
- https://github.com/vercel-labs/tersa
- https://github.com/vercel-labs/deep-research-template
- https://github.com/vercel-labs/lead-agent
