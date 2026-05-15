# Domain Error Patterns

## Core Concept

Domain errors represent failures that occur within the domain layer. Using Effect's `Data.TaggedError`, we create structured, type-safe errors with discriminated unions for precise error handling.

## Error Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    Domain Error Hierarchy                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ValueError                                                 │
│    └─ Invalid inputs, failed validation, format errors      │
│                                                             │
│  InvariantError                                             │
│    └─ Business rule violations, state transition failures   │
│                                                             │
│  StateError                                                 │
│    └─ Entity not found, unexpected state conditions         │
│                                                             │
│  AllocationError                                            │
│    └─ Resource creation failures (ID generation, etc.)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Basic Error Structure

### ValueError - Input Validation Failures

```ts
import { Data } from "effect";

export class OrderValueError extends Data.TaggedError("OrderValueError")<{
  readonly reason:
    | "order_id_empty"
    | "order_id_invalid"
    | "amount_invalid"
    | "date_invalid"
    | "quantity_negative";
  readonly message: string;
}> {}
```

### InvariantError - Business Rule Violations

```ts
export class OrderInvariantError extends Data.TaggedError("OrderInvariantError")<{
  readonly reason:
    | "cancellation_not_allowed"
    | "shipment_not_allowed"
    | "modification_not_allowed"
    | "payment_already_processed";
  readonly message: string;
}> {}
```

### StateError - Entity State Issues

```ts
export class OrderStateError extends Data.TaggedError("OrderStateError")<{
  readonly reason:
    | "order_not_found"
    | "customer_not_found"
    | "product_unavailable";
  readonly message: string;
}> {}
```

### AllocationError - Resource Creation Failures

```ts
export class OrderIdAllocationError extends Data.TaggedError("OrderIdAllocationError")<{
  readonly cause: unknown;
}> {}
```

## Union Type for All Domain Errors

Always export a union type that encompasses all errors in the domain:

```ts
export type OrderDomainError =
  | OrderValueError
  | OrderInvariantError
  | OrderStateError
  | OrderIdAllocationError;
```

## Error Design Principles

### 1. Reason Codes as Literal Unions

Use narrow literal types for reasons to enable exhaustive pattern matching:

```ts
// Good: Specific, enumerable reasons
readonly reason:
  | "order_id_empty"
  | "order_id_invalid"
  | "amount_negative";

// Bad: Open-ended string
readonly reason: string;
```

### 2. Reason Naming Convention

```
<entity>_<field>_<failure_type>

Examples:
- order_id_empty
- order_amount_negative
- user_email_invalid
- payment_status_not_allowed
```

### 3. Message Field for Human-Readable Details

```ts
// Include context in the message
new OrderValueError({
  reason: "amount_negative",
  message: `order amount must be positive, got: ${amount}`,
})

// Include entity identifiers when relevant
new OrderInvariantError({
  reason: "cancellation_not_allowed",
  message: `cannot cancel order ${orderId} in ${currentPhase} phase`,
})
```

## Error Helper Functions

### Simple Fail Helper

```ts
const fail = <R extends OrderValueError["reason"]>(reason: R, message: string) =>
  Effect.fail(new OrderValueError({ reason, message }));

// Usage
return fail("order_id_empty", "order id must not be blank");
```

### Invariant Failure Helper

```ts
const invariantFailure = (
  reason: OrderInvariantError["reason"],
  currentPhase: Phase,
  messageBuilder: (phase: Phase) => string,
) =>
  new OrderInvariantError({
    reason,
    message: messageBuilder(currentPhase),
  });

// Usage
Effect.fail(
  invariantFailure(
    "cancellation_not_allowed",
    aggregate.phase,
    (phase) => `cannot cancel order while in ${phase} phase`,
  ),
);
```

### Error Mapper for Schema Decode

```ts
const mapParseError =
  (reason: OrderValueError["reason"], message: string) =>
  (_error: unknown) =>
    new OrderValueError({ reason, message });

// Usage
Schema.decodeUnknown(OrderIdSchema)(value).pipe(
  Effect.mapError(mapParseError("order_id_invalid", "invalid order id format")),
);
```

## Error Handling Patterns

### Pattern Matching with Match

```ts
import { Match } from "effect";

const handleError = (error: OrderDomainError) =>
  Match.value(error).pipe(
    Match.tag("OrderValueError", (e) => ({
      type: "validation",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderInvariantError", (e) => ({
      type: "business_rule",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderStateError", (e) => ({
      type: "not_found",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderIdAllocationError", (e) => ({
      type: "system",
      code: "allocation_failed",
      message: String(e.cause),
    })),
    Match.exhaustive,
  );
```

### Catching Specific Error Types

```ts
import { Effect } from "effect";

const processOrder = (orderId: string) =>
  pipe(
    findOrder(orderId),
    Effect.catchTag("OrderStateError", (error) =>
      error.reason === "order_not_found"
        ? Effect.succeed(createNewOrder(orderId))
        : Effect.fail(error),
    ),
  );
```

### Transforming Errors for API Response

```ts
const toApiError = (error: OrderDomainError): ApiErrorResponse =>
  Match.value(error).pipe(
    Match.tag("OrderValueError", (e) => ({
      status: 400,
      error: "VALIDATION_ERROR",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderInvariantError", (e) => ({
      status: 409,
      error: "CONFLICT",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderStateError", (e) => ({
      status: 404,
      error: "NOT_FOUND",
      code: e.reason,
      message: e.message,
    })),
    Match.tag("OrderIdAllocationError", () => ({
      status: 500,
      error: "INTERNAL_ERROR",
      code: "id_allocation_failed",
      message: "Failed to generate order ID",
    })),
    Match.exhaustive,
  );
```

## Multi-Domain Error Composition

When working with multiple domains, compose error unions:

```ts
// order/errors.ts
export type OrderDomainError = OrderValueError | OrderInvariantError | OrderStateError;

// payment/errors.ts
export type PaymentDomainError = PaymentValueError | PaymentInvariantError;

// application layer
type ApplicationError = OrderDomainError | PaymentDomainError;

const handleApplicationError = (error: ApplicationError) =>
  Match.value(error).pipe(
    Match.tag("OrderValueError", ...),
    Match.tag("OrderInvariantError", ...),
    Match.tag("OrderStateError", ...),
    Match.tag("PaymentValueError", ...),
    Match.tag("PaymentInvariantError", ...),
    Match.exhaustive,
  );
```

## Error with Additional Context

For errors that need extra contextual data:

```ts
export class OrderValidationError extends Data.TaggedError("OrderValidationError")<{
  readonly reason: "line_items_invalid" | "total_mismatch";
  readonly message: string;
  readonly details: ReadonlyArray<{
    readonly field: string;
    readonly issue: string;
  }>;
}> {}

// Usage
new OrderValidationError({
  reason: "line_items_invalid",
  message: "one or more line items are invalid",
  details: [
    { field: "items[0].quantity", issue: "must be positive" },
    { field: "items[2].price", issue: "exceeds maximum allowed" },
  ],
});
```

## Best Practices

### DO

- Use narrow literal unions for reason codes
- Include contextual information in messages
- Create separate error classes for each category (Value, Invariant, State)
- Export a union type of all domain errors
- Keep error definitions close to the domain they represent

### DON'T

- Don't use generic `Error` or `string` for domain errors
- Don't throw exceptions; use `Effect.fail`
- Don't include stack traces in domain error data
- Don't expose internal implementation details in error messages
- Don't create overly broad error types (keep them domain-specific)

## Testing Domain Errors

```ts
import { Effect, Either } from "effect";

const runEither = <A, E>(effect: Effect.Effect<A, E>) =>
  Effect.runPromise(Effect.either(effect));

describe("Order domain errors", () => {
  test("returns ValueError for invalid order id", async () => {
    const result = await runEither(makeOrderId(""));

    expect(Either.isLeft(result)).toBe(true);
    if (Either.isLeft(result)) {
      expect(result.left).toBeInstanceOf(OrderValueError);
      expect(result.left).toMatchObject({
        _tag: "OrderValueError",
        reason: "order_id_empty",
      });
    }
  });

  test("returns InvariantError for invalid state transition", async () => {
    const order = createCompletedOrder();
    const result = await runEither(cancelOrder(order));

    expect(Either.isLeft(result)).toBe(true);
    if (Either.isLeft(result)) {
      expect(result.left).toBeInstanceOf(OrderInvariantError);
      expect(result.left.reason).toBe("cancellation_not_allowed");
    }
  });
});
```

## Error Organization in File Structure

```
src/domain/order/
├── errors.ts          # All error definitions
├── valueObjects.ts    # Uses ValueError
├── aggregate.ts       # Uses InvariantError, StateError
├── numbering.ts       # Uses AllocationError
└── index.ts           # Re-exports errors
```
