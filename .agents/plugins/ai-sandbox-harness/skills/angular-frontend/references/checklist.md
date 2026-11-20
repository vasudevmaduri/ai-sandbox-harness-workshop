# Angular Frontend Reference Checklist

## Review Checklist
- [ ] `standalone: true` and `ChangeDetectionStrategy.OnPush` on every component
- [ ] `@for` blocks always specify a unique `track` expression
- [ ] Zero `any` in TypeScript files or templates
- [ ] Subscriptions cleaned up via `takeUntilDestroyed()` or `toSignal()`
- [ ] HTTP error paths tested with `HttpTestingController`
