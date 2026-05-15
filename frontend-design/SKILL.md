---
name: frontend-design
description: Generate Feature-Sliced Design (FSD) components for frontendv2. Use when creating pages, features, entities, widgets, or shared modules following FSD architecture with React Router v7 + Effect + Tailwind CSS.
---

# Feature-Sliced Design (FSD) for frontendv2

## Overview

Feature-Sliced Design is an architectural methodology for scaffolding frontend applications. This skill generates type-safe, modular code following FSD principles with the project's tech stack:

- **React Router v7** (file-based routing)
- **Effect** (functional composition, error handling)
- **Tailwind CSS v4** + **shadcn/ui** (styling)
- **TypeScript** (strict typing)

## FSD Layer Hierarchy

Modules can only import from layers **strictly below**:

```
┌─────────────────────────────────────────────┐
│  app/         Application bootstrap          │ ← Top (most coupled)
├─────────────────────────────────────────────┤
│  pages/       Full page compositions         │
├─────────────────────────────────────────────┤
│  widgets/     Large self-contained UI blocks │
├─────────────────────────────────────────────┤
│  features/    User interactions & actions    │
├─────────────────────────────────────────────┤
│  entities/    Business domain objects        │
├─────────────────────────────────────────────┤
│  shared/      Reusable utilities & UI kit    │ ← Bottom (most reusable)
└─────────────────────────────────────────────┘
```

## When to Use

| Task                                               | Layer    |
| -------------------------------------------------- | -------- |
| Add a new route/page                               | pages    |
| Create a reusable business feature (login, search) | features |
| Model a domain concept (user, video, account)      | entities |
| Build a large composite UI block (sidebar, header) | widgets  |
| Add UI components, utilities, API client           | shared   |
| Configure providers, global styles                 | app      |

## Directory Structure

```
frontendv2/app/
├── app/                    # App layer
│   ├── providers/          # Context providers
│   ├── styles/             # Global styles
│   └── index.ts
├── pages/                  # Pages layer
│   └── {page-name}/
│       ├── ui/             # Page UI components
│       ├── api/            # Loaders, actions
│       ├── model/          # Page-specific state
│       └── index.ts        # Public API
├── widgets/                # Widgets layer
│   └── {widget-name}/
│       ├── ui/
│       └── index.ts
├── features/               # Features layer
│   └── {feature-name}/
│       ├── ui/             # Feature UI
│       ├── api/            # Feature API calls
│       ├── model/          # Feature state/logic
│       └── index.ts
├── entities/               # Entities layer
│   └── {entity-name}/
│       ├── ui/             # Entity UI representations
│       ├── api/            # Entity CRUD operations
│       ├── model/          # Entity types & logic
│       └── index.ts
├── shared/                 # Shared layer
│   ├── ui/                 # UI kit (shadcn/ui)
│   ├── api/                # API client, fetchers
│   ├── lib/                # Utilities
│   ├── config/             # Environment, constants
│   └── types/              # Shared type definitions
└── routes/                 # React Router route files
    └── *.tsx               # Bridge to pages layer
```

## Segment Naming Convention

Each slice contains segments organized by **purpose** (why), not by **type** (what):

| Segment   | Purpose                  | NOT                      |
| --------- | ------------------------ | ------------------------ |
| `ui/`     | Visual representation    | `components/`            |
| `api/`    | External communication   | `services/`, `fetchers/` |
| `model/`  | Business logic, state    | `store/`, `hooks/`       |
| `lib/`    | Internal utilities       | `utils/`, `helpers/`     |
| `config/` | Configuration, constants | `constants/`             |

## Implementation Workflow

### 1. Entity Creation

```
Input: Entity name, fields, API operations
Output: Entity slice with model, api, ui segments
```

See: `references/entities.md`

### 2. Feature Creation

```
Input: Feature name, user action, required entities
Output: Feature slice with complete workflow
```

See: `references/features.md`

### 3. Page Creation

```
Input: Page name, route, composed features/widgets
Output: Page slice + route file
```

See: `references/pages.md`

### 4. Widget Creation

```
Input: Widget name, composed entities/features
Output: Widget slice with ui segment
```

See: `references/widgets.md`

## Migration from application/

Mapping from current `application/` structure to FSD:

| application/         | frontendv2/ (FSD)             |
| -------------------- | ----------------------------- |
| `domain/`            | `entities/{entity}/model/`    |
| `workflow/`          | `features/{feature}/model/`   |
| `repository/`        | `entities/{entity}/api/`      |
| `gateway/`           | `shared/api/`                 |
| `components/ui/`     | `shared/ui/`                  |
| `components/common/` | `shared/ui/` or `widgets/`    |
| `utils/`             | `shared/lib/`                 |
| `types/`             | `shared/types/`               |
| `hooks/`             | Distribute to relevant slices |
| `routes/`            | `routes/` + `pages/`          |

## Quick Reference Templates

### Entity Template

```ts
// entities/user/model/types.ts
export type UserId = string & { readonly _brand: "UserId" };
export type User = {
  readonly id: UserId;
  readonly email: string;
  readonly name: string;
  readonly status: UserStatus;
};

// entities/user/model/index.ts
export * from "./types";
export * from "./validators";

// entities/user/index.ts (Public API)
export { type User, type UserId } from "./model";
export { UserCard, UserAvatar } from "./ui";
export { userApi } from "./api";
```

### Feature Template

```ts
// features/auth/login/model/login.workflow.ts
import { Effect } from "effect";
import { userApi } from "@/entities/user";
import { sessionApi } from "@/shared/api";

export class LoginWorkflow extends Effect.Service<LoginWorkflow>()(
  "@features/auth/login",
  {
    effect: Effect.gen(function* () {
      return {
        execute: (credentials: Credentials) =>
          Effect.gen(function* () {
            const user = yield* userApi.authenticate(credentials);
            yield* sessionApi.create(user.id);
            return user;
          }),
      };
    }),
  }
) {}

// features/auth/login/index.ts (Public API)
export { LoginForm } from "./ui";
export { LoginWorkflow } from "./model";
```

### Page Template

```ts
// pages/login/ui/LoginPage.tsx
import { LoginForm } from "@/features/auth/login";

export function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoginForm />
    </div>
  );
}

// routes/login.tsx (React Router route file)
import { LoginPage } from "@/pages/login";
import type { Route } from "./+types/login";

export async function loader({ request }: Route.LoaderArgs) {
  // redirect if already logged in
}

export async function action({ request }: Route.ActionArgs) {
  // handle login form submission
}

export default function Login() {
  return <LoginPage />;
}
```

## Import Rules

```ts
// CORRECT: Import from lower layers only
// In features/auth/login/ui/LoginForm.tsx
import { Button } from "@/shared/ui"; // shared (lower)
import { User, UserAvatar } from "@/entities/user"; // entities (lower)

// INCORRECT: Never import from same or higher layers
import { SignupForm } from "@/features/auth/signup"; // same layer slice
import { Header } from "@/widgets/header"; // higher layer
import { Dashboard } from "@/pages/dashboard"; // higher layer
```

## Public API Pattern

Every slice MUST have an `index.ts` that explicitly exports its public API:

```ts
// features/auth/login/index.ts
// Only export what other slices need
export { LoginForm } from "./ui/LoginForm";
export { LoginWorkflow } from "./model/login.workflow";
export type { LoginCredentials } from "./model/types";

// Internal files are NOT exported
// ./ui/LoginFormField.tsx  (internal)
// ./model/validators.ts     (internal)
```

## Effect Integration Pattern

Use Effect for business logic in `model/` segments:

```ts
// entities/user/model/user.validators.ts
import { Effect, Schema } from "effect";
import { ValidationError } from "@/shared/lib/errors";

export const EmailSchema = Schema.String.pipe(
  Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
  Schema.brand("Email")
);

export type Email = typeof EmailSchema.Type;

export const makeEmail = (value: string) =>
  Schema.decodeUnknown(EmailSchema)(value.toLowerCase().trim()).pipe(
    Effect.mapError(() => new ValidationError({ reason: "invalid_email" }))
  );
```

## References

- `references/entities.md` - Entity patterns, domain modeling
- `references/features.md` - Feature workflows, user actions
- `references/pages.md` - Page composition, routing integration
- `references/widgets.md` - Widget patterns, composition strategies
- `references/shared.md` - Shared utilities, UI kit, API client

## Memo

- Use barrel import
- Use `type` rather than `interface`
- Export type and public API at the bottom of file
- For every function, Add JSdocument
- Always add error logging for effect related operation
- use code for UI handling
- use shared api path in page
