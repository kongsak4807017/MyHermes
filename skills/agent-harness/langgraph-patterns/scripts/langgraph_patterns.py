#!/usr/bin/env python3
"""
LangGraph-style patterns for stateful agent workflows.
Pure Python implementation without external dependencies.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import json


@dataclass
class State:
    """Base state class for graph execution."""
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value
    
    def to_dict(self) -> dict:
        return {
            "data": self.data,
            "history": self.history,
            "error": self.error,
        }


class Node:
    """Graph node that processes state."""
    
    def __init__(self, name: str, func: Callable[[State], State]):
        self.name = name
        self.func = func
        self.edges: List['Edge'] = []
    
    def add_edge(self, edge: 'Edge'):
        self.edges.append(edge)
    
    def run(self, state: State) -> State:
        state.history.append(self.name)
        try:
            return self.func(state)
        except Exception as e:
            state.error = f"Error in {self.name}: {str(e)}"
            return state


class Edge:
    """Edge connecting nodes with optional condition."""
    
    def __init__(self, target: str, condition: Optional[Callable[[State], bool]] = None):
        self.target = target
        self.condition = condition
    
    def should_follow(self, state: State) -> bool:
        if self.condition is None:
            return True
        return self.condition(state)


class Graph:
    """Directed graph for agent workflow execution."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.entry_point: Optional[str] = None
    
    def add_node(self, name: str, func: Callable[[State], State]) -> Node:
        """Add a node to the graph."""
        node = Node(name, func)
        self.nodes[name] = node
        if self.entry_point is None:
            self.entry_point = name
        return node
    
    def add_edge(self, source: str, target: str,
                 condition: Optional[Callable[[State], bool]] = None):
        """Add an edge between nodes."""
        if source not in self.nodes:
            raise ValueError(f"Source node '{source}' not found")
        
        edge = Edge(target, condition)
        self.nodes[source].add_edge(edge)
    
    def add_conditional_edge(self, source: str, router: Callable[[State], str]):
        """Add a conditional edge that routes based on state."""
        if source not in self.nodes:
            raise ValueError(f"Source node '{source}' not found")
        
        def condition_factory(target):
            return lambda state: router(state) == target
        
        # Add edges to all possible targets
        for target in self.nodes:
            if target != source:
                edge = Edge(target, condition_factory(target))
                self.nodes[source].add_edge(edge)
    
    def set_entry_point(self, name: str):
        """Set the entry point node."""
        if name not in self.nodes:
            raise ValueError(f"Node '{name}' not found")
        self.entry_point = name
    
    def run(self, state: Optional[State] = None, max_steps: int = 100) -> State:
        """Execute the graph starting from entry point."""
        if state is None:
            state = State()
        
        if self.entry_point is None:
            raise ValueError("No entry point set")
        
        current = self.entry_point
        visited: Set[str] = set()
        steps = 0
        
        while current and steps < max_steps:
            steps += 1
            
            if current in visited and not self._has_cycle_exit(current):
                state.error = f"Cycle detected at {current}"
                break
            
            visited.add(current)
            
            # Run node
            node = self.nodes[current]
            state = node.run(state)
            
            if state.error:
                break
            
            # Find next node
            next_node = None
            for edge in node.edges:
                if edge.should_follow(state):
                    next_node = edge.target
                    break
            
            current = next_node
        
        if steps >= max_steps:
            state.error = "Max steps exceeded"
        
        return state
    
    def _has_cycle_exit(self, node_name: str) -> bool:
        """Check if a node has an exit from a cycle."""
        node = self.nodes[node_name]
        for edge in node.edges:
            if edge.target != node_name:
                return True
        return False
    
    def visualize(self) -> str:
        """Generate Mermaid diagram."""
        lines = ["graph TD"]
        
        for name, node in self.nodes.items():
            for edge in node.edges:
                label = "conditional" if edge.condition else ""
                lines.append(f"    {name} -->|{label}| {edge.target}")
        
        return "\n".join(lines)


# Pre-built patterns

class ReActPattern:
    """ReAct pattern: Reasoning + Acting loop."""
    
    @staticmethod
    def create(graph: Graph, tools: Dict[str, Callable]):
        """Create a ReAct pattern in the graph."""
        
        def think(state: State) -> State:
            state.set("thought", f"Thinking about: {state.get('input')}")
            state.set("needs_tool", len(state.get("steps", [])) < 3)
            return state
        
        def act(state: State) -> State:
            tool_name = state.get("tool_name")
            if tool_name and tool_name in tools:
                result = tools[tool_name](state.get("tool_input"))
                state.set("tool_result", result)
                steps = state.get("steps", [])
                steps.append({"tool": tool_name, "result": result})
                state.set("steps", steps)
            return state
        
        def observe(state: State) -> State:
            state.set("observation", f"Result: {state.get('tool_result')}")
            return state
        
        def respond(state: State) -> State:
            state.set("response", f"Answer based on {state.get('steps', [])}")
            return state
        
        graph.add_node("think", think)
        graph.add_node("act", act)
        graph.add_node("observe", observe)
        graph.add_node("respond", respond)
        
        graph.add_edge("think", "act", lambda s: s.get("needs_tool", False))
        graph.add_edge("think", "respond", lambda s: not s.get("needs_tool", False))
        graph.add_edge("act", "observe")
        graph.add_edge("observe", "think")
        
        graph.set_entry_point("think")
        
        return graph


class PlanAndExecutePattern:
    """Plan and execute pattern."""
    
    @staticmethod
    def create(graph: Graph, executor: Callable):
        """Create a plan-and-execute pattern."""
        
        def plan(state: State) -> State:
            state.set("plan", ["step1", "step2", "step3"])
            state.set("current_step", 0)
            return state
        
        def execute(state: State) -> State:
            plan = state.get("plan", [])
            current = state.get("current_step", 0)
            
            if current < len(plan):
                result = executor(plan[current])
                state.set(f"result_{current}", result)
                state.set("current_step", current + 1)
            
            return state
        
        def check_done(state: State) -> State:
            plan = state.get("plan", [])
            current = state.get("current_step", 0)
            state.set("done", current >= len(plan))
            return state
        
        def finalize(state: State) -> State:
            results = [state.get(f"result_{i}") for i in range(len(state.get("plan", [])))]
            state.set("final_result", results)
            return state
        
        graph.add_node("plan", plan)
        graph.add_node("execute", execute)
        graph.add_node("check_done", check_done)
        graph.add_node("finalize", finalize)
        
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", "check_done")
        graph.add_edge("check_done", "execute", lambda s: not s.get("done", False))
        graph.add_edge("check_done", "finalize", lambda s: s.get("done", False))
        
        graph.set_entry_point("plan")
        
        return graph


if __name__ == "__main__":
    # Demo: Simple graph
    graph = Graph()
    
    def start(state: State) -> State:
        state.set("value", 1)
        return state
    
    def double(state: State) -> State:
        state.set("value", state.get("value") * 2)
        return state
    
    def end(state: State) -> State:
        state.set("final", state.get("value"))
        return state
    
    graph.add_node("start", start)
    graph.add_node("double", double)
    graph.add_node("end", end)
    
    graph.add_edge("start", "double")
    graph.add_edge("double", "end")
    
    graph.set_entry_point("start")
    
    result = graph.run()
    print("Simple Graph Result:", result.to_dict())
    
    # Demo: ReAct pattern
    react_graph = Graph()
    tools = {
        "search": lambda x: f"Results for {x}",
    }
    ReActPattern.create(react_graph, tools)
    
    state = State()
    state.set("input", "What is AI?")
    state.set("tool_name", "search")
    state.set("tool_input", "AI definition")
    
    result = react_graph.run(state)
    print("\nReAct Result:", result.to_dict())
    
    # Visualize
    print("\nMermaid Diagram:")
    print(react_graph.visualize())
