---
name: vercel-web-interface-guidelines
description: "Web interface guidelines and patterns from Vercel Labs: UI/UX best practices, component patterns, and design systems."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs/web-interface-guidelines)
license: MIT
dependencies: [react, css, design-systems]
metadata:
  hermes:
    tags: [UI, UX, Design, Web Interface, Guidelines, Vercel]
---

# Vercel Web Interface Guidelines

UI/UX guidelines and patterns extracted from vercel-labs/web-interface-guidelines and related repos.

## When to use

**Use when:**
- Building web interfaces that need to feel modern and polished
- Creating design systems
- Implementing responsive layouts
- Building accessible components
- Need Vercel-style UI patterns

## Core Principles

### 1. Simplicity
- Reduce cognitive load
- One primary action per view
- Progressive disclosure

### 2. Consistency
- Reuse components
- Consistent spacing (4px grid)
- Predictable interactions

### 3. Feedback
- Loading states
- Success/error feedback
- Skeleton screens

### 4. Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support

## Patterns

### Pattern 1: Loading States

```tsx
// components/skeleton.tsx
export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  );
}

// Usage with Suspense
<Suspense fallback={<Skeleton className="h-32 w-full" />}>
  <DataComponent />
</Suspense>
```

### Pattern 2: Command Palette

```tsx
// components/command-palette.tsx
'use client';
import { useState, useEffect } from 'react';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(true);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Command>
        <CommandInput placeholder="Type a command..." />
        <CommandList>
          <CommandItem>Go to Dashboard</CommandItem>
          <CommandItem>Go to Settings</CommandItem>
        </CommandList>
      </Command>
    </Dialog>
  );
}
```

### Pattern 3: Toast Notifications

```tsx
// hooks/use-toast.ts
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  
  const toast = (message: string, type: 'success' | 'error') => {
    const id = Math.random().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };
  
  return { toasts, toast };
}
```

### Pattern 4: Responsive Data Table

```tsx
// components/data-table.tsx
export function DataTable<T>({ data, columns }: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key} className="text-left p-2">
                {col.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-t">
              {columns.map(col => (
                <td key={col.key} className="p-2">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## References

- https://github.com/vercel-labs/web-interface-guidelines
