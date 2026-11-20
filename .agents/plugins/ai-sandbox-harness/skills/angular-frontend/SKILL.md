---
name: angular-frontend
description: Production workflow for modern Angular (17+) applications using standalone components, Signals, OnPush change detection, strict TypeScript, and deterministic unit specs.
---

# Angular Frontend Skill

Use this skill when authoring Angular components, services, routes, or state. Consult [references/checklist.md](./references/checklist.md) for Signal and testing patterns.

## 1. Modern Angular Architecture
- **Standalone Only**: All components, directives, and pipes MUST set `standalone: true` (no new `NgModule` declarations).
- **Signals-First State**: Prefer `signal()`, `computed()`, `input()`, and `output()` over manual `BehaviorSubject` boilerplate for synchronous UI state.
- **Change Detection**: Default every component to `ChangeDetectionStrategy.OnPush` and use native `@if`, `@for (item of items(); track item.id)`, and `@switch` control flow.
- **Strict TypeScript**: Zero `any` types, zero non-null `!` hacks on API payloads; model contracts with explicit `readonly` interfaces.
- **Service Isolation**: Place `HttpClient` calls and state mutations in `providedIn: 'root'` services injected via `inject()`.

## 2. Verification Protocol
1. Add `.spec.ts` unit tests covering component rendering, Signal state transitions, and mocked `HttpTestingController` error states.
2. Run `ng lint` and `ng test --watch=false` before finishing.
