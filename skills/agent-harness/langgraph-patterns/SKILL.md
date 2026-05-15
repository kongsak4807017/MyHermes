---
name: langgraph-patterns
description: "Graph-based stateful agent patterns: nodes, edges, state machines, and conditional routing for complex agent workflows."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LangGraph, State Machine, Graph, Workflow, Agent Orchestration, Stateful, Conditional Routing]
---

# LangGraph Patterns for Agent Workflows

## What's inside

Graph-based stateful agent patterns: nodes, edges, state machines, conditional routing, and cycles for complex agent workflows.

## Quick start

```python
from langgraph_patterns import Graph, State

# Define state
class AgentState(State):
    messages: list = []
    next_step: str = "start"

# Create graph
graph = Graph()

# Add nodes
@graph.node("start")
def start_node(state: AgentState):
    state.messages.append("Starting...")
    state.next_step = "process"
    return state

@graph.node("process")
def process_node(state: AgentState):
    state.messages.append("Processing...")
    state.next_step = "end"
    return state

@graph.node("end")
def end_node(state: AgentState):
    state.messages.append("Done!")
    return state

# Add edges
graph.add_edge("start", "process")
graph.add_edge("process", "end")

# Run
result = graph.run(AgentState())
print(result.messages)  # ["Starting...", "Processing...", "Done!"]
```

## Common workflows

### Workflow 1: Conditional Routing

```python
@graph.node("router")
def router_node(state: AgentState):
    if state.needs_tool:
        state.next_step = "tool"
    else:
        state.next_step = "respond"
    return state

graph.add_conditional_edge("router", lambda s: s.next_step)
```

### Workflow 2: Loop with Max Iterations

```python
@graph.node("agent")
def agent_node(state: AgentState):
    state.iteration += 1
    if state.iteration >= state.max_iterations:
        state.next_step = "end"
    else:
        state.next_step = "agent"
    return state

graph.add_edge("agent", "agent")  # Self-loop
```

### Workflow 3: Parallel Execution

```python
@graph.node("parallel_a")
def parallel_a(state: AgentState):
    state.result_a = task_a()
    return state

@graph.node("parallel_b")
def parallel_b(state: AgentState):
    state.result_b = task_b()
    return state

@graph.node("merge")
def merge(state: AgentState):
    state.combined = combine(state.result_a, state.result_b)
    return state

graph.add_parallel_edges(["parallel_a", "parallel_b"], "merge")
```

## Patterns

| Pattern | Use Case |
|---------|----------|
| Linear | Simple sequential workflows |
| Conditional | Decision-based routing |
| Loop | Iterative processes |
| Parallel | Concurrent execution |
| Subgraph | Modular components |

## Resources

- LangGraph: https://github.com/langchain-ai/langgraph
- LangChain: https://python.langchain.com
