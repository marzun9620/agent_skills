# Entities Layer

## Overview

Entities represent **business domain objects** - the core concepts that the application manipulates. Examples: User, Video, Account, Report, TikTokAccount.

## Structure

```
entities/
└── {entity-name}/
    ├── model/              # Types, validation, business logic
    │   ├── types.ts        # Type definitions
    │   ├── validators.ts   # Schema validation with Effect
    │   └── index.ts        # Re-exports
    ├── api/                # CRUD operations
    │   ├── {entity}.api.ts # API functions
    │   └── index.ts
    ├── ui/                 # Entity UI representations
    │   ├── {Entity}Card.tsx
    │   ├── {Entity}Avatar.tsx
    │   └── index.ts
    └── index.ts            # Public API
```

## Implementation Pattern

### 1. Model Segment

#### types.ts - Type Definitions

```ts
// entities/user/model/types.ts
import { Brand } from "effect";

// Branded ID type
export type UserId = string & Brand.Brand<"UserId">;

// Status enum
export const UserStatus = {
  INVITED: "INVITED",
  ACTIVE: "ACTIVE",
  EXPIRED: "EXPIRED",
} as const;
export type UserStatus = (typeof UserStatus)[keyof typeof UserStatus];

// Role enum
export const UserRole = {
  SERVICE_ADMIN: "SERVICE_ADMIN",
  OWNER: "OWNER",
  MEMBER: "MEMBER",
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

// Entity type (immutable)
export type User = {
  readonly id: UserId;
  readonly email: string;
  readonly name: string;
  readonly companyId: string;
  readonly status: UserStatus;
  readonly role: UserRole;
};

// Discriminated unions for state-specific behavior
export type InvitedUser = User & { readonly status: typeof UserStatus.INVITED };
export type ActiveUser = User & { readonly status: typeof UserStatus.ACTIVE };
export type ExpiredUser = User & { readonly status: typeof UserStatus.EXPIRED };
```

#### validators.ts - Schema Validation

```ts
// entities/user/model/validators.ts
import { Effect, Schema } from "effect";
import { ValidationError } from "@/shared/lib/errors";
import type { UserId } from "./types";

// Branded schema
export const UserIdSchema = Schema.String.pipe(
  Schema.minLength(1),
  Schema.brand("UserId")
);

export const EmailSchema = Schema.String.pipe(
  Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
  Schema.brand("Email")
);

// Smart constructors
export const makeUserId = (value: string): Effect.Effect<UserId, ValidationError> =>
  Schema.decodeUnknown(UserIdSchema)(value).pipe(
    Effect.mapError(() => new ValidationError({ reason: "invalid_user_id" }))
  );

export const makeEmail = (value: string): Effect.Effect<string, ValidationError> =>
  Schema.decodeUnknown(EmailSchema)(value.toLowerCase().trim()).pipe(
    Effect.mapError(() => new ValidationError({ reason: "invalid_email" }))
  );

// Type guards
export const isActiveUser = (user: User): user is ActiveUser =>
  user.status === "ACTIVE";

export const isInvitedUser = (user: User): user is InvitedUser =>
  user.status === "INVITED";
```

#### Pure Domain Functions

```ts
// entities/user/model/operations.ts
import type { User, ActiveUser, InvitedUser, ExpiredUser } from "./types";
import { UserStatus, UserRole } from "./types";

// State transitions (pure functions)
export const activateUser = (user: InvitedUser): ActiveUser => ({
  ...user,
  status: UserStatus.ACTIVE,
});

export const expireUser = (user: ActiveUser): ExpiredUser => ({
  ...user,
  status: UserStatus.EXPIRED,
});

// Business logic (pure functions)
export const canTransferOwnership = (
  currentOwner: User,
  targetMember: User
): boolean =>
  currentOwner.role === UserRole.OWNER &&
  targetMember.role === UserRole.MEMBER &&
  currentOwner.status === UserStatus.ACTIVE &&
  targetMember.status === UserStatus.ACTIVE &&
  currentOwner.companyId === targetMember.companyId;
```

### 2. API Segment

```ts
// entities/user/api/user.api.ts
import { Effect } from "effect";
import { ApiClient } from "@/shared/api";
import type { User, UserId } from "../model";

export class UserApi extends Effect.Service<UserApi>()("@entities/user/api", {
  effect: Effect.gen(function* () {
    const client = yield* ApiClient;

    return {
      getById: (id: UserId) =>
        client.get<User>(`/users/${id}`),

      getByEmail: (email: string) =>
        client.get<User | null>(`/users/by-email/${encodeURIComponent(email)}`),

      update: (id: UserId, data: Partial<User>) =>
        client.patch<User>(`/users/${id}`, data),
    };
  }),
  dependencies: [ApiClient.Default],
}) {}

// Convenience export
export const userApi = UserApi;
```

### 3. UI Segment

```ts
// entities/user/ui/UserCard.tsx
import type { User } from "../model";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { UserAvatar } from "./UserAvatar";

type UserCardProps = {
  readonly user: User;
  readonly onClick?: () => void;
};

export function UserCard({ user, onClick }: UserCardProps) {
  return (
    <Card className="cursor-pointer hover:shadow-md" onClick={onClick}>
      <CardHeader>
        <div className="flex items-center gap-3">
          <UserAvatar user={user} />
          <CardTitle>{user.name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{user.email}</p>
        <span className="text-xs px-2 py-1 rounded-full bg-secondary">
          {user.role}
        </span>
      </CardContent>
    </Card>
  );
}
```

```ts
// entities/user/ui/UserAvatar.tsx
import type { User } from "../model";

type UserAvatarProps = {
  readonly user: User;
  readonly size?: "sm" | "md" | "lg";
};

export function UserAvatar({ user, size = "md" }: UserAvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-16 h-16 text-lg",
  };

  const initials = user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-primary text-primary-foreground flex items-center justify-center font-medium`}
    >
      {initials}
    </div>
  );
}
```

### 4. Public API (index.ts)

```ts
// entities/user/index.ts

// Types (public)
export type { User, UserId, ActiveUser, InvitedUser, ExpiredUser } from "./model";
export { UserStatus, UserRole } from "./model";

// Validators (public)
export { makeUserId, makeEmail, isActiveUser, isInvitedUser } from "./model";

// Domain operations (public)
export { activateUser, expireUser, canTransferOwnership } from "./model";

// API (public)
export { UserApi, userApi } from "./api";

// UI (public)
export { UserCard, UserAvatar } from "./ui";
```

## Entity from application/domain Migration

### Original (application/domain/user.ts)

```ts
// application/app/domain/user.ts
export type UserId = string;
export type User = { ... };
export const hashPassword = (...) => Effect.tryPromise(...);
export const isValidPassword = (...) => Effect.tryPromise(...);
```

### Migrated (entities/user/)

```
entities/user/
├── model/
│   ├── types.ts         # UserId, User types
│   ├── validators.ts    # makeUserId, makeEmail
│   ├── operations.ts    # activateUser, expireUser
│   └── index.ts
├── api/
│   ├── user.api.ts      # CRUD operations
│   └── index.ts
├── ui/
│   ├── UserCard.tsx
│   ├── UserAvatar.tsx
│   └── index.ts
└── index.ts
```

## Key Principles

1. **Immutability**: All entity fields are `readonly`
2. **Type Safety**: Use branded types for IDs
3. **Pure Functions**: Domain logic should have no side effects
4. **Effect for I/O**: Use Effect for validation and API calls
5. **Explicit Exports**: Only export what's needed via index.ts
6. **No Cross-Slice Imports**: Entities cannot import from other entities

## Common Entities in <your-app>

Based on `application/domain/`:

| Entity            | Purpose                       |
| ----------------- | ----------------------------- |
| `user`            | User accounts and roles       |
| `company`         | Company/organization          |
| `tiktok-account`  | Linked TikTok accounts        |
| `video`           | TikTok video metadata         |
| `video-summary`   | Aggregated video statistics   |
| `report`          | Analytics reports             |
| `session`         | User sessions                 |
| `token`           | Authentication tokens         |
