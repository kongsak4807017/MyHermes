# SocratiCode Dependency Graph System

## Supported Languages (4 languages)
- dart
- lua
- svelte
- vue

## Graph Analysis Functions
- `getFileDependencies()`
- `findCircularDependencies()`
- `getGraphStats()`
- `generateMermaidDiagram()`

## Key Capabilities
- Import extraction via ast-grep (AST parsing)
- Circular dependency detection (DFS-based)
- Graph statistics: total files, edges, most connected, orphans
- Blast radius calculation (reverse transitive closure)
- Call-flow tracing (forward DFS from entry points)
- Symbol-level resolution (function/class level, not just file)

## Data Structure
```typescript
interface CodeGraph {
  nodes: Array<{
    relativePath: string;
    language: string;
    dependencies: string[];  // files this node imports
    dependents: string[];    // files that import this node
  }>;
}
```
