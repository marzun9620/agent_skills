# Aggregate Patterns

## Core Concept

An **Aggregate** is a consistency boundary - a cluster of domain objects that must remain consistent together. The **Aggregate Root** is the single entry point for all modifications.

This guide covers two levels:

1. **Basic Aggregate Root** - Pure state + invariant enforcement (no events)
2. **Event-Driven Aggregate** - With domain events and commands (optional extension)

---

# Part 1: Basic Aggregate Root

## Principles

- **Single Entry Point**: All modifications go through the Aggregate Root
- **Invariant Enforcement**: Business rules are checked on every mutation
- **Immutability**: Return new instances instead of mutating
- **Pure Functions**: Transitions return `Effect<Aggregate, Error>`

## Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Aggregate Root                           │
├─────────────────────────────────────────────────────────────┤
│  State (readonly)                                           │
│    ├─ id: EntityId                                          │
│    ├─ ...domain fields                                      │
│    └─ revision: number (optional, for optimistic locking)   │
│                                                             │
│  Invariants                                                 │
│    └─ Business rules that must always hold                  │
│                                                             │
│  Operations                                                 │
│    └─ Methods that modify state while preserving invariants │
└─────────────────────────────────────────────────────────────┘
```

## Basic Aggregate Definition

### 1. Type Definition

```ts
import { Effect } from "effect";
import { OrderId, CustomerId, MoneyAmount } from "./valueObjects.ts";
import { OrderInvariantError, OrderValueError } from "./errors.ts";

export type OrderItem = {
  readonly productId: string;
  readonly name: string;
  readonly quantity: number;
  readonly unitPrice: MoneyAmount;
};

export type Order = {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  readonly items: ReadonlyArray<OrderItem>;
  readonly discount: MoneyAmount;
  readonly note?: string;
};
```

### 2. Derived Properties (Computed from State)

```ts
// Pure functions that derive values from aggregate state
export const calculateSubtotal = (order: Order): number =>
  order.items.reduce(
    (sum, item) => sum + item.quantity * item.unitPrice,
    0,
  );

export const calculateTotal = (order: Order): number =>
  Math.max(0, calculateSubtotal(order) - order.discount);

export const getItemCount = (order: Order): number =>
  order.items.reduce((sum, item) => sum + item.quantity, 0);
```

### 3. Invariant Checks

```ts
// Invariants are predicates that must always be true
const ensureHasItems = (order: Order) =>
  order.items.length === 0
    ? Effect.fail(
        new OrderInvariantError({
          reason: "items_required",
          message: "order must have at least one item",
        }),
      )
    : Effect.succeed(order);

const ensurePositiveQuantities = (order: Order) => {
  const invalid = order.items.find((item) => item.quantity <= 0);
  return invalid
    ? Effect.fail(
        new OrderInvariantError({
          reason: "quantity_invalid",
          message: `item "${invalid.name}" has invalid quantity: ${invalid.quantity}`,
        }),
      )
    : Effect.succeed(order);
};

const ensureDiscountNotExceedsSubtotal = (order: Order) => {
  const subtotal = calculateSubtotal(order);
  return order.discount > subtotal
    ? Effect.fail(
        new OrderInvariantError({
          reason: "discount_exceeds_subtotal",
          message: `discount ${order.discount} exceeds subtotal ${subtotal}`,
        }),
      )
    : Effect.succeed(order);
};

// Combine all invariants
const validateInvariants = (order: Order) =>
  Effect.gen(function* () {
    yield* ensureHasItems(order);
    yield* ensurePositiveQuantities(order);
    yield* ensureDiscountNotExceedsSubtotal(order);
    return order;
  });
```

### 4. Factory Function (Creation)

```ts
export const createOrder = (
  id: OrderId,
  customerId: CustomerId,
  items: ReadonlyArray<OrderItem>,
) =>
  Effect.gen(function* () {
    const order: Order = {
      id,
      customerId,
      items,
      discount: 0 as MoneyAmount,
    };

    // Validate invariants on creation
    yield* validateInvariants(order);

    return order;
  });
```

### 5. Operations (Mutations)

```ts
// Add item to order
export const addItem = (order: Order, item: OrderItem) =>
  Effect.gen(function* () {
    // Validate input
    if (item.quantity <= 0) {
      yield* Effect.fail(
        new OrderValueError({
          reason: "quantity_invalid",
          message: "quantity must be positive",
        }),
      );
    }

    // Check if item already exists
    const existingIndex = order.items.findIndex(
      (i) => i.productId === item.productId,
    );

    const updatedItems =
      existingIndex >= 0
        ? order.items.map((i, idx) =>
            idx === existingIndex
              ? { ...i, quantity: i.quantity + item.quantity }
              : i,
          )
        : [...order.items, item];

    const updated: Order = { ...order, items: updatedItems };

    // Validate invariants after mutation
    yield* validateInvariants(updated);

    return updated;
  });

// Remove item from order
export const removeItem = (order: Order, productId: string) =>
  Effect.gen(function* () {
    const updatedItems = order.items.filter((i) => i.productId !== productId);

    const updated: Order = { ...order, items: updatedItems };

    yield* validateInvariants(updated);

    return updated;
  });

// Apply discount
export const applyDiscount = (order: Order, discount: MoneyAmount) =>
  Effect.gen(function* () {
    const updated: Order = { ...order, discount };

    yield* validateInvariants(updated);

    return updated;
  });

// Update note
export const updateNote = (order: Order, note: string | undefined) =>
  Effect.succeed({ ...order, note } satisfies Order);
```

## Aggregate with Lifecycle Status

When an aggregate has distinct states (not a full state machine):

```ts
export type OrderStatus = "draft" | "confirmed" | "cancelled";

export type Order = {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  readonly status: OrderStatus;
  readonly items: ReadonlyArray<OrderItem>;
  readonly confirmedAt?: Date;
  readonly cancelledAt?: Date;
  readonly cancellationReason?: string;
};

// Status-aware operations
export const confirmOrder = (order: Order) =>
  Effect.gen(function* () {
    if (order.status !== "draft") {
      yield* Effect.fail(
        new OrderInvariantError({
          reason: "invalid_status",
          message: `cannot confirm order in ${order.status} status`,
        }),
      );
    }

    yield* ensureHasItems(order);

    return {
      ...order,
      status: "confirmed",
      confirmedAt: new Date(),
    } satisfies Order;
  });

export const cancelOrder = (order: Order, reason: string) =>
  Effect.gen(function* () {
    if (order.status === "cancelled") {
      yield* Effect.fail(
        new OrderInvariantError({
          reason: "already_cancelled",
          message: "order is already cancelled",
        }),
      );
    }

    return {
      ...order,
      status: "cancelled",
      cancelledAt: new Date(),
      cancellationReason: reason,
    } satisfies Order;
  });
```

## Nested Entities within Aggregate

```ts
export type OrderLineId = string & { readonly _brand: "OrderLineId" };

export type OrderLine = {
  readonly id: OrderLineId;
  readonly productId: string;
  readonly quantity: number;
  readonly unitPrice: MoneyAmount;
};

export type Order = {
  readonly id: OrderId;
  readonly lines: ReadonlyArray<OrderLine>;
};

// Operations on nested entities go through the root
export const updateLineQuantity = (
  order: Order,
  lineId: OrderLineId,
  quantity: number,
) =>
  Effect.gen(function* () {
    const lineIndex = order.lines.findIndex((l) => l.id === lineId);

    if (lineIndex === -1) {
      yield* Effect.fail(
        new OrderInvariantError({
          reason: "line_not_found",
          message: `line ${lineId} not found`,
        }),
      );
    }

    if (quantity <= 0) {
      yield* Effect.fail(
        new OrderValueError({
          reason: "quantity_invalid",
          message: "quantity must be positive",
        }),
      );
    }

    const updatedLines = order.lines.map((line, idx) =>
      idx === lineIndex ? { ...line, quantity } : line,
    );

    return { ...order, lines: updatedLines } satisfies Order;
  });
```

## Optimistic Locking

```ts
export type Order = {
  readonly id: OrderId;
  readonly version: number; // Incremented on each change
  readonly items: ReadonlyArray<OrderItem>;
};

// Wrapper that increments version
const withVersionIncrement = <A extends { version: number }>(
  aggregate: A,
): A => ({
  ...aggregate,
  version: aggregate.version + 1,
});

export const addItem = (order: Order, item: OrderItem) =>
  Effect.gen(function* () {
    const updated = { ...order, items: [...order.items, item] };
    yield* validateInvariants(updated);
    return withVersionIncrement(updated);
  });
```

---

# Part 2: Event-Driven Aggregate (Optional Extension)

When you need to track what happened (audit, event sourcing, CQRS):

## Extended Structure

```ts
import { Data } from "effect";

// Domain Events
export class OrderCreated extends Data.TaggedClass("OrderCreated")<{
  readonly orderId: OrderId;
  readonly customerId: CustomerId;
}> {}

export class ItemAdded extends Data.TaggedClass("ItemAdded")<{
  readonly orderId: OrderId;
  readonly item: OrderItem;
}> {}

export type OrderEvent = OrderCreated | ItemAdded;

// Commands for side effects
export type SendConfirmationEmail = {
  readonly _tag: "SendConfirmationEmail";
  readonly orderId: OrderId;
};

export type OrderCommand = SendConfirmationEmail;

// Result type with events and commands
export type AggregateResult<A> = {
  readonly aggregate: A;
  readonly events: readonly OrderEvent[];
  readonly commands: readonly OrderCommand[];
};

const result = <A>(
  aggregate: A,
  events: readonly OrderEvent[] = [],
  commands: readonly OrderCommand[] = [],
): AggregateResult<A> => ({ aggregate, events, commands });
```

## Event-Emitting Operations

```ts
export const createOrder = (
  id: OrderId,
  customerId: CustomerId,
  items: ReadonlyArray<OrderItem>,
) =>
  Effect.gen(function* () {
    const order: Order = { id, customerId, items, discount: 0 as MoneyAmount };
    yield* validateInvariants(order);

    return result(order, [new OrderCreated({ orderId: id, customerId })]);
  });

export const addItem = (order: Order, item: OrderItem) =>
  Effect.gen(function* () {
    const updated = { ...order, items: [...order.items, item] };
    yield* validateInvariants(updated);

    return result(updated, [new ItemAdded({ orderId: order.id, item })]);
  });
```

---

## Best Practices

### DO

- Define clear aggregate boundaries
- Enforce all invariants on every mutation
- Keep aggregates small and focused
- Use readonly for immutability
- Return new instances, never mutate

### DON'T

- Don't allow direct access to internal entities
- Don't skip invariant validation
- Don't call external services from aggregates
- Don't create "god aggregates" that do too much

## Testing

```ts
import { Effect, Either } from "effect";

const run = Effect.runPromise;
const runEither = <A, E>(effect: Effect.Effect<A, E>) =>
  Effect.runPromise(Effect.either(effect));

describe("Order aggregate", () => {
  test("creates order with items", async () => {
    const order = await run(createOrder(id, customerId, [item]));
    expect(order.items).toHaveLength(1);
  });

  test("rejects order without items", async () => {
    const result = await runEither(createOrder(id, customerId, []));
    expect(Either.isLeft(result)).toBe(true);
  });

  test("adds item to existing order", async () => {
    const order = await run(createOrder(id, customerId, [item1]));
    const updated = await run(addItem(order, item2));
    expect(updated.items).toHaveLength(2);
  });

  test("rejects discount exceeding subtotal", async () => {
    const order = await run(createOrder(id, customerId, [item]));
    const result = await runEither(applyDiscount(order, 99999 as MoneyAmount));
    expect(Either.isLeft(result)).toBe(true);
  });
});
```

## File Organization

```
src/domain/order/
├── aggregate.ts       # Aggregate type + operations
├── errors.ts          # InvariantError, ValueError
├── valueObjects.ts    # OrderId, CustomerId, MoneyAmount
└── index.ts           # Public exports

# If using events (optional)
├── events.ts          # Domain events
└── commands.ts        # Side effect commands
```
