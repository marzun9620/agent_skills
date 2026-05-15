# ValueObject Patterns

## Core Concept

ValueObjects are immutable domain primitives identified by their value, not identity. In Effect, we implement them using:

1. **Branded Schema** - Compile-time type safety via TypeScript brands
2. **Smart Constructor** - Runtime validation returning `Effect<T, Error>`
3. **Normalization** - Input sanitization before validation

## Pattern Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      ValueObject                            │
├─────────────────────────────────────────────────────────────┤
│  Schema (XxxSchema)                                         │
│    └─ Base type + Constraints + Brand                       │
│                                                             │
│  Type (Xxx)                                                 │
│    └─ typeof XxxSchema.Type                                 │
│                                                             │
│  Constructor (makeXxx)                                      │
│    └─ normalize → validate → Effect<Xxx, DomainValueError>  │
└─────────────────────────────────────────────────────────────┘
```

## Basic ValueObjects

### String Identifier

```ts
import { Effect, Schema } from "effect";
import { DomainValueError } from "./errors.ts";

// Schema with brand
export const UserIdSchema = Schema.String.pipe(
  Schema.minLength(1),
  Schema.brand("UserId"),
);

// Type alias
export type UserId = typeof UserIdSchema.Type;

// Helper for error creation
const fail = (reason: DomainValueError["reason"], message: string) =>
  Effect.fail(new DomainValueError({ reason, message }));

// Smart constructor
export const makeUserId = (value: string) => {
  const trimmed = value.trim();
  return trimmed.length === 0
    ? fail("user_id_empty", "user id must not be blank")
    : Schema.decodeUnknown(UserIdSchema)(trimmed).pipe(
        Effect.mapError(() =>
          new DomainValueError({
            reason: "user_id_invalid",
            message: "invalid user id format",
          }),
        ),
      );
};
```

### Numeric Value

```ts
export const MoneyAmountSchema = Schema.Number.pipe(
  Schema.brand("MoneyAmount"),
);

export type MoneyAmount = typeof MoneyAmountSchema.Type;

export const makeMoneyAmount = (value: number) =>
  !Number.isFinite(value)
    ? fail("money_amount_invalid", "amount must be a finite number")
    : Schema.decodeUnknown(MoneyAmountSchema)(value).pipe(
        Effect.mapError(() =>
          new DomainValueError({
            reason: "money_amount_invalid",
            message: "invalid money amount",
          }),
        ),
      );
```

### Constrained Numeric

```ts
export const PercentageSchema = Schema.Number.pipe(
  Schema.greaterThanOrEqualTo(0),
  Schema.lessThanOrEqualTo(100),
  Schema.brand("Percentage"),
);

export type Percentage = typeof PercentageSchema.Type;

export const makePercentage = (value: number) =>
  Schema.decodeUnknown(PercentageSchema)(value).pipe(
    Effect.mapError(() =>
      new DomainValueError({
        reason: "percentage_invalid",
        message: "percentage must be between 0 and 100",
      }),
    ),
  );
```

## Pattern-Based ValueObjects

### Email Address

```ts
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const EmailSchema = Schema.String.pipe(
  Schema.pattern(emailPattern),
  Schema.brand("Email"),
);

export type Email = typeof EmailSchema.Type;

export const makeEmail = (value: string) => {
  const normalized = value.trim().toLowerCase();
  return normalized.length === 0
    ? fail("email_empty", "email must not be blank")
    : Schema.decodeUnknown(EmailSchema)(normalized).pipe(
        Effect.mapError(() =>
          new DomainValueError({
            reason: "email_invalid",
            message: `invalid email format: ${value}`,
          }),
        ),
      );
};
```

### ISO Date String

```ts
const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;

export const IsoDateSchema = Schema.String.pipe(
  Schema.pattern(isoDatePattern),
  Schema.brand("IsoDate"),
);

export type IsoDate = typeof IsoDateSchema.Type;

// Additional semantic validation
const isValidIsoDate = (iso: string): boolean => {
  const date = new Date(`${iso}T00:00:00.000Z`);
  return !Number.isNaN(date.getTime()) && date.toISOString().startsWith(iso);
};

export const makeIsoDate = (value: string) =>
  Effect.flatMap(
    Schema.decodeUnknown(IsoDateSchema)(value).pipe(
      Effect.mapError(() =>
        new DomainValueError({
          reason: "iso_date_invalid",
          message: `invalid ISO date format: ${value}`,
        }),
      ),
    ),
    (iso) =>
      isValidIsoDate(iso)
        ? Effect.succeed(iso)
        : fail("iso_date_invalid", `invalid date value: ${value}`),
  );
```

### Slug / URL-Safe String

```ts
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export const SlugSchema = Schema.String.pipe(
  Schema.minLength(1),
  Schema.maxLength(100),
  Schema.pattern(slugPattern),
  Schema.brand("Slug"),
);

export type Slug = typeof SlugSchema.Type;

export const makeSlug = (value: string) => {
  const normalized = value.trim().toLowerCase();
  return Schema.decodeUnknown(SlugSchema)(normalized).pipe(
    Effect.mapError(() =>
      new DomainValueError({
        reason: "slug_invalid",
        message: "slug must contain only lowercase letters, numbers, and hyphens",
      }),
    ),
  );
};
```

## Composite ValueObjects

### Address (Multiple Fields)

```ts
export const AddressSchema = Schema.Struct({
  street: Schema.String.pipe(Schema.minLength(1), Schema.maxLength(200)),
  city: Schema.String.pipe(Schema.minLength(1), Schema.maxLength(100)),
  postalCode: Schema.String.pipe(Schema.pattern(/^\d{3}-?\d{4}$/)),
  country: Schema.String.pipe(Schema.minLength(2), Schema.maxLength(2)),
}).pipe(Schema.brand("Address"));

export type Address = typeof AddressSchema.Type;

export const makeAddress = (input: {
  street: string;
  city: string;
  postalCode: string;
  country: string;
}) =>
  Schema.decodeUnknown(AddressSchema)({
    street: input.street.trim(),
    city: input.city.trim(),
    postalCode: input.postalCode.replace("-", "").replace(/(\d{3})(\d{4})/, "$1-$2"),
    country: input.country.trim().toUpperCase(),
  }).pipe(
    Effect.mapError(() =>
      new DomainValueError({
        reason: "address_invalid",
        message: "invalid address format",
      }),
    ),
  );
```

### Money (Amount + Currency)

```ts
export const CurrencySchema = Schema.Literal("JPY", "USD", "EUR");
export type Currency = typeof CurrencySchema.Type;

export const MoneySchema = Schema.Struct({
  amount: MoneyAmountSchema,
  currency: CurrencySchema,
}).pipe(Schema.brand("Money"));

export type Money = typeof MoneySchema.Type;

export const makeMoney = (amount: number, currency: string) =>
  Effect.gen(function* () {
    const validAmount = yield* makeMoneyAmount(amount);
    const validCurrency = yield* Schema.decodeUnknown(CurrencySchema)(currency).pipe(
      Effect.mapError(() =>
        new DomainValueError({
          reason: "currency_invalid",
          message: `unsupported currency: ${currency}`,
        }),
      ),
    );

    return yield* Schema.decodeUnknown(MoneySchema)({
      amount: validAmount,
      currency: validCurrency,
    }).pipe(
      Effect.mapError(() =>
        new DomainValueError({
          reason: "money_invalid",
          message: "invalid money value",
        }),
      ),
    );
  });
```

## Reusable Decoder Factory

For repetitive patterns, create a factory function:

```ts
const decode =
  <A>(
    schema: Schema.Schema<A, string>,
    reason: DomainValueError["reason"],
    message: string,
  ) =>
  (value: string) =>
    value.length === 0
      ? fail(reason, message)
      : Schema.decodeUnknown(schema)(value).pipe(
          Effect.mapError(() => new DomainValueError({ reason, message })),
        );

// Usage
export const makeOrderId = decode(
  OrderIdSchema,
  "order_id_invalid",
  "order id must not be empty",
);

export const makeProductId = decode(
  ProductIdSchema,
  "product_id_invalid",
  "product id must not be empty",
);
```

## Validation Beyond Schema

Sometimes you need validation logic that Schema alone cannot express:

```ts
export const makeDateRange = (start: string, end: string) =>
  Effect.gen(function* () {
    const startDate = yield* makeIsoDate(start);
    const endDate = yield* makeIsoDate(end);

    // Cross-field validation
    if (new Date(endDate).getTime() < new Date(startDate).getTime()) {
      yield* fail("date_range_invalid", "end date must be after start date");
    }

    return { start: startDate, end: endDate } as const;
  });
```

## Best Practices

### DO

- Always use `readonly` in composite types
- Normalize inputs before validation (trim, lowercase, etc.)
- Return specific error reasons for each failure mode
- Include the invalid value in error messages when helpful
- Keep ValueObjects immutable and side-effect free

### DON'T

- Don't throw exceptions; return `Effect.fail`
- Don't allow construction without validation (no public constructors)
- Don't mutate ValueObjects; create new instances
- Don't include business logic in ValueObjects (they're data carriers)
- Don't depend on infrastructure in ValueObject modules

## Testing ValueObjects

```ts
import { Effect, Either } from "effect";

const run = Effect.runPromise;
const runEither = <A, E>(effect: Effect.Effect<A, E>) =>
  Effect.runPromise(Effect.either(effect));

describe("makeEmail", () => {
  test("accepts valid email", async () => {
    const result = await run(makeEmail("user@example.com"));
    expect(result).toBe("user@example.com");
  });

  test("normalizes to lowercase", async () => {
    const result = await run(makeEmail("USER@EXAMPLE.COM"));
    expect(result).toBe("user@example.com");
  });

  test("rejects empty string", async () => {
    const result = await runEither(makeEmail(""));
    expect(Either.isLeft(result)).toBe(true);
    if (Either.isLeft(result)) {
      expect(result.left.reason).toBe("email_empty");
    }
  });

  test("rejects invalid format", async () => {
    const result = await runEither(makeEmail("not-an-email"));
    expect(Either.isLeft(result)).toBe(true);
    if (Either.isLeft(result)) {
      expect(result.left.reason).toBe("email_invalid");
    }
  });
});
```
