---
name: domain-design
description: Generate DDD building blocks (ValueObject, Error, Aggregate) using Effect + Schema. Use when creating new domain types, defining custom errors, or modeling aggregate lifecycles with invariant enforcement in /backendv2 folder.
---

# Domain Building Blocks

## Overview

Generate type-safe, immutable domain primitives using Effect ecosystem patterns:

- **ValueObject**: Branded types with Schema validation and smart constructors
- **Error**: Tagged errors with structured reasons for precise error handling
- **Aggregate**: State machines with lifecycle phases, invariant guards, and event/command emission

## When to Use

| Task                                                         | Use This Skill |
| ------------------------------------------------------------ | -------------- |
| Create a new identifier type (UserId, OrderId, etc.)         | ValueObject    |
| Define a constrained primitive (Email, MoneyAmount, IsoDate) | ValueObject    |
| Model domain validation failures                             | Error          |
| Model business rule violations                               | Error          |
| Design an entity with lifecycle states                       | Aggregate      |
| Enforce state transition rules                               | Aggregate      |

## TDD Workflow

ドメインビルディングブロックは TDD（テスト駆動開発）で実装する。

### Red-Green-Refactor Cycle

```
1. Red    → 失敗するテストを書く（期待する振る舞いを定義）
2. Green  → テストを通す最小限の実装
3. Refactor → コードを整理（テストは緑のまま）
```

### TDD for ValueObject

```ts
// 1. RED: テストを先に書く
describe("makeEmail", () => {
  test("accepts valid email", async () => {
    const result = await run(makeEmail("user@example.com"));
    expect(result).toBe("user@example.com");
  });

  test("rejects empty string", async () => {
    const result = await runEither(makeEmail(""));
    expect(Either.isLeft(result)).toBe(true);
  });

  test("rejects invalid format", async () => {
    const result = await runEither(makeEmail("not-an-email"));
    expect(Either.isLeft(result)).toBe(true);
  });
});

// 2. GREEN: テストを通す実装
// 3. REFACTOR: 正規化、エラーメッセージ改善など
```

### TDD for Aggregate

```ts
// 1. RED: インバリアントの振る舞いをテストで定義
describe("Order aggregate", () => {
  test("rejects order without items", async () => {
    const result = await runEither(createOrder(id, customerId, []));
    expect(Either.isLeft(result)).toBe(true);
    if (Either.isLeft(result)) {
      expect(result.left.reason).toBe("items_required");
    }
  });

  test("rejects discount exceeding subtotal", async () => {
    const order = await run(createOrder(id, customerId, [item]));
    const result = await runEither(applyDiscount(order, 99999));
    expect(Either.isLeft(result)).toBe(true);
  });
});

// 2. GREEN: インバリアントを実装
// 3. REFACTOR: ensureXxx関数に抽出
```

### Test Utilities

```ts
import { Effect, Either } from "effect";

export const run = Effect.runPromise;

export const runEither = <A, E>(effect: Effect.Effect<A, E>) =>
  Effect.runPromise(Effect.either(effect));
```

---

## Implementation Workflow

### 1. ValueObject Creation

```
Input: Name, base type, constraints, validation rules
Output: Schema, Type alias, makeX constructor
```

1. Define the branded Schema with constraints
2. Export the Type alias
3. Implement `makeX` smart constructor returning `Effect<T, DomainValueError>`
4. Add normalization (trim, lowercase, etc.) if needed

See: `references/value-objects.md`

### 2. Error Definition

```
Input: Error category, reason codes, context fields
Output: TaggedError class with typed reasons
```

1. Choose error category (Value, Invariant, State, Allocation)
2. Define reason codes as literal union
3. Create TaggedError class with structured payload
4. Export union type for all domain errors

See: `references/domain-errors.md`

### 3. Aggregate Modeling

```
Input: Entity name, fields, invariants, (optional) status/events
Output: Aggregate type, invariant checks, operations
```

**Basic Aggregate Root** (default):

1. Define aggregate type with readonly fields
2. Identify invariants (business rules that must always hold)
3. Implement `validateInvariants` combining all checks
4. Create factory function with invariant validation
5. Implement operations that validate invariants after mutation

**Event-Driven Extension** (when needed): 6. Add domain events (TaggedClass) for tracking changes 7. Add commands for side effects 8. Return `AggregateResult<A>` with events/commands

See: `references/aggregates.md`

## Quick Reference

### ValueObject Template

```ts
import { Effect, Schema } from "effect";
import { DomainValueError } from "./errors.ts";

// 1. Schema
export const XxxSchema = Schema.String.pipe(
  Schema.minLength(1),
  Schema.brand("Xxx")
);

// 2. Type
export type Xxx = typeof XxxSchema.Type;

// 3. Constructor
export const makeXxx = (value: string) =>
  Schema.decodeUnknown(XxxSchema)(value.trim()).pipe(
    Effect.mapError(
      () =>
        new DomainValueError({
          reason: "xxx_invalid",
          message: "invalid xxx value",
        })
    )
  );
```

### Error Template

```ts
import { Data } from "effect";

export class DomainValueError extends Data.TaggedError("DomainValueError")<{
  readonly reason: "xxx_invalid" | "yyy_empty";
  readonly message: string;
}> {}
```

### Aggregate Root Template

```ts
// Type
export type Order = {
  readonly id: OrderId;
  readonly items: ReadonlyArray<OrderItem>;
  readonly discount: MoneyAmount;
};

// Invariant
const ensureHasItems = (order: Order) =>
  order.items.length === 0
    ? Effect.fail(
        new OrderInvariantError({ reason: "items_required", message: "..." })
      )
    : Effect.succeed(order);

// Operation
export const addItem = (order: Order, item: OrderItem) =>
  Effect.gen(function* () {
    const updated = { ...order, items: [...order.items, item] };
    yield* ensureHasItems(updated);
    return updated;
  });
```

## References

- `references/value-objects.md` - ValueObject patterns, complex types, composition
- `references/domain-errors.md` - Error categorization, reason design, error unions
- `references/aggregates.md` - Aggregate Root basics, invariants, event-driven extension
