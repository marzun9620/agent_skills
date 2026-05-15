# Features Layer

## Overview

Features implement **user actions and interactions** - the things users can do in the application. Examples: Login, Signup, CreateReport, ConnectTikTokAccount.

Features compose entities and shared resources to deliver complete user workflows.

## Structure

```
features/
└── {feature-name}/
    ├── model/                  # Business logic & state
    │   ├── {feature}.workflow.ts  # Effect-based workflow
    │   ├── types.ts            # Feature-specific types
    │   └── index.ts
    ├── api/                    # Feature-specific API calls
    │   ├── {feature}.api.ts
    │   └── index.ts
    ├── ui/                     # Feature UI components
    │   ├── {Feature}Form.tsx
    │   ├── {Feature}Button.tsx
    │   └── index.ts
    └── index.ts                # Public API
```

## Implementation Pattern

### 1. Model Segment - Workflow

```ts
// features/auth/login/model/login.workflow.ts
import { Effect } from "effect";
import { UserApi, type User } from "@/entities/user";
import { SessionApi } from "@/shared/api";
import { AuthError, ValidationError } from "@/shared/lib/errors";
import type { LoginCredentials, LoginResult } from "./types";

// Composed mini-workflows using Effect.Service
export class VerifyUserExistsWorkflow extends Effect.Service<VerifyUserExistsWorkflow>()(
  "@features/auth/login/verify-user",
  {
    effect: Effect.gen(function* () {
      const userApi = yield* UserApi;

      return {
        execute: (email: string) =>
          Effect.gen(function* () {
            const user = yield* userApi.getByEmail(email);
            if (!user) {
              return yield* Effect.fail(
                new AuthError({ reason: "user_not_found" })
              );
            }
            return user;
          }),
      };
    }),
    dependencies: [UserApi.Default],
  }
) {}

export class VerifyPasswordWorkflow extends Effect.Service<VerifyPasswordWorkflow>()(
  "@features/auth/login/verify-password",
  {
    effect: Effect.gen(function* () {
      return {
        execute: (user: User, password: string) =>
          Effect.gen(function* () {
            // Password verification logic using Effect
            const isValid = yield* verifyPassword(user.passwordHash, password);
            if (!isValid) {
              return yield* Effect.fail(
                new AuthError({ reason: "invalid_password" })
              );
            }
            return user;
          }),
      };
    }),
  }
) {}

// Main workflow composing mini-workflows
export class LoginWorkflow extends Effect.Service<LoginWorkflow>()(
  "@features/auth/login",
  {
    effect: Effect.gen(function* () {
      const verifyUserExists = yield* VerifyUserExistsWorkflow;
      const verifyPassword = yield* VerifyPasswordWorkflow;
      const sessionApi = yield* SessionApi;

      return {
        execute: (credentials: LoginCredentials): Effect.Effect<LoginResult, AuthError | ValidationError> =>
          Effect.gen(function* () {
            // 1. Verify user exists
            const user = yield* verifyUserExists.execute(credentials.email);

            // 2. Verify password
            yield* verifyPassword.execute(user, credentials.password);

            // 3. Create session
            const session = yield* sessionApi.create(user.id);

            return {
              user,
              session,
              redirectTo: credentials.redirectTo ?? "/dashboard",
            };
          }),
      };
    }),
    dependencies: [
      VerifyUserExistsWorkflow.Default,
      VerifyPasswordWorkflow.Default,
      SessionApi.Default,
    ],
  }
) {}
```

### 2. Model Segment - Types

```ts
// features/auth/login/model/types.ts
import type { User } from "@/entities/user";
import type { Session } from "@/shared/api";

export type LoginCredentials = {
  readonly email: string;
  readonly password: string;
  readonly redirectTo?: string;
  readonly remember?: boolean;
};

export type LoginResult = {
  readonly user: User;
  readonly session: Session;
  readonly redirectTo: string;
};

// Form state type for UI
export type LoginFormState = {
  readonly email: string;
  readonly password: string;
  readonly isSubmitting: boolean;
  readonly errors: {
    email?: string;
    password?: string;
    form?: string;
  };
};
```

### 3. API Segment (if needed)

```ts
// features/auth/login/api/login.api.ts
import { Effect } from "effect";
import { ApiClient } from "@/shared/api";
import type { LoginCredentials, LoginResult } from "../model";

// Feature-specific API endpoint
export class LoginApi extends Effect.Service<LoginApi>()(
  "@features/auth/login/api",
  {
    effect: Effect.gen(function* () {
      const client = yield* ApiClient;

      return {
        authenticate: (credentials: LoginCredentials) =>
          client.post<LoginResult>("/auth/login", credentials),
      };
    }),
    dependencies: [ApiClient.Default],
  }
) {}
```

### 4. UI Segment

```ts
// features/auth/login/ui/LoginForm.tsx
import { useActionData, Form } from "react-router";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

type LoginFormProps = {
  readonly redirectTo?: string;
};

export function LoginForm({ redirectTo = "/dashboard" }: LoginFormProps) {
  const actionData = useActionData<{ errors?: Record<string, string> }>();

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Login</CardTitle>
      </CardHeader>
      <CardContent>
        <Form method="post" className="space-y-4">
          <input type="hidden" name="redirectTo" value={redirectTo} />

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
            />
            {actionData?.errors?.email && (
              <p className="text-sm text-destructive">{actionData.errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
            />
            {actionData?.errors?.password && (
              <p className="text-sm text-destructive">{actionData.errors.password}</p>
            )}
          </div>

          {actionData?.errors?.form && (
            <p className="text-sm text-destructive">{actionData.errors.form}</p>
          )}

          <Button type="submit" className="w-full">
            Sign In
          </Button>
        </Form>
      </CardContent>
    </Card>
  );
}
```

```ts
// features/auth/login/ui/index.ts
export { LoginForm } from "./LoginForm";
```

### 5. Public API

```ts
// features/auth/login/index.ts

// Workflow (for use in route actions)
export { LoginWorkflow } from "./model";

// Types
export type { LoginCredentials, LoginResult, LoginFormState } from "./model";

// UI
export { LoginForm } from "./ui";
```

## Feature Organization

### Grouping Related Features

```
features/
├── auth/                    # Auth feature group
│   ├── login/
│   ├── logout/
│   ├── signup/
│   ├── reset-password/
│   └── verify-email/
├── account/                 # Account feature group
│   ├── connect-tiktok/
│   ├── disconnect-tiktok/
│   └── update-profile/
├── video/                   # Video feature group
│   ├── search-videos/
│   └── filter-videos/
└── report/                  # Report feature group
    ├── create-report/
    └── export-report/
```

### Feature Group Index

```ts
// features/auth/index.ts
export * from "./login";
export * from "./logout";
export * from "./signup";
// ...
```

## Migration from application/workflow

### Original (application/workflow/auth/login.server.ts)

```ts
// Workflow classes defined inline
export class LoginWorkflow extends Effect.Service<LoginWorkflow>()(...) { ... }
export const login = (request: Request) => ...;
```

### Migrated Structure

```
features/auth/login/
├── model/
│   ├── login.workflow.ts    # Workflow classes
│   ├── types.ts             # Credentials, Result types
│   └── index.ts
├── ui/
│   ├── LoginForm.tsx        # Form component
│   └── index.ts
└── index.ts                 # Public API
```

## Route Integration

Features are consumed in route files:

```ts
// routes/login.tsx
import { LoginForm, LoginWorkflow } from "@/features/auth/login";
import { Effect } from "effect";
import type { Route } from "./+types/login";

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();

  const result = await Effect.runPromise(
    Effect.gen(function* () {
      const workflow = yield* LoginWorkflow;
      return yield* workflow.execute({
        email: formData.get("email") as string,
        password: formData.get("password") as string,
        redirectTo: formData.get("redirectTo") as string,
      });
    }).pipe(
      Effect.provide(LoginWorkflow.Default),
      Effect.either
    )
  );

  if (Either.isLeft(result)) {
    return { errors: { form: result.left.message } };
  }

  return redirect(result.right.redirectTo, {
    headers: {
      "Set-Cookie": await sessionCookie.serialize(result.right.session),
    },
  });
}

export default function LoginRoute() {
  return <LoginForm />;
}
```

## Key Principles

1. **User-Centric**: Features map to user actions, not technical concerns
2. **Composition**: Features compose entities and shared resources
3. **Effect Workflows**: Use Effect.Service for dependency injection
4. **Isolated**: Features cannot import from other features
5. **Complete**: Each feature contains all it needs (UI, logic, API)

## Common Features in <your-app>

Based on `application/workflow/`:

| Feature Group | Features                                    |
| ------------- | ------------------------------------------- |
| `auth`        | login, logout, signup, reset-password, verify-email, accept-invitation |
| `accounts`    | connect-tiktok, disconnect-tiktok, list-accounts |
| `videos`      | search-videos, filter-videos, video-details |
| `reports`     | create-report, view-report, export-report   |
| `settings`    | update-profile, change-password, manage-totp |
| `dashboard`   | view-dashboard, refresh-metrics             |
| `contact`     | submit-contact-form                         |
