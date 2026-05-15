# Shared Layer

## Overview

Shared is the **foundation layer** containing reusable utilities, UI components, API clients, and configuration that all other layers depend on. It has no business logic.

## Structure

```
shared/
├── ui/                     # UI kit (shadcn/ui components)
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── index.ts
├── api/                    # API client and utilities
│   ├── client.ts           # HTTP client
│   ├── session.ts          # Session management
│   └── index.ts
├── lib/                    # Utilities
│   ├── utils.ts            # General utilities (cn, etc.)
│   ├── errors.ts           # Error classes
│   ├── date.ts             # Date utilities
│   └── index.ts
├── config/                 # Configuration
│   ├── env.ts              # Environment variables
│   ├── routes.ts           # Route constants
│   └── index.ts
└── types/                  # Shared type definitions
    ├── api.ts              # API response types
    └── index.ts
```

## UI Segment (shadcn/ui)

### Button Component

```ts
// shared/ui/button.tsx
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

### UI Index

```ts
// shared/ui/index.ts
export { Button, buttonVariants, type ButtonProps } from "./button";
export { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from "./card";
export { Input } from "./input";
export { Label } from "./label";
export { Checkbox } from "./checkbox";
export { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./dialog";
export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip";
// ... more components
```

## API Segment

### HTTP Client with Effect

```ts
// shared/api/client.ts
import { Effect, Context, Layer } from "effect";
import { ApiError, NetworkError, UnauthorizedError } from "@/shared/lib/errors";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type RequestConfig = {
  readonly headers?: Record<string, string>;
  readonly body?: unknown;
};

export class ApiClient extends Effect.Service<ApiClient>()("@shared/api/client", {
  effect: Effect.gen(function* () {
    const baseUrl = yield* Effect.sync(() =>
      typeof window !== "undefined" ? "" : process.env.API_URL ?? ""
    );

    const request = <T>(
      method: HttpMethod,
      path: string,
      config?: RequestConfig
    ): Effect.Effect<T, ApiError | NetworkError | UnauthorizedError> =>
      Effect.tryPromise({
        try: async () => {
          const response = await fetch(`${baseUrl}${path}`, {
            method,
            headers: {
              "Content-Type": "application/json",
              ...config?.headers,
            },
            body: config?.body ? JSON.stringify(config.body) : undefined,
          });

          if (!response.ok) {
            if (response.status === 401) {
              throw new UnauthorizedError();
            }
            throw new ApiError({
              status: response.status,
              message: await response.text(),
            });
          }

          return response.json() as Promise<T>;
        },
        catch: (error) => {
          if (error instanceof ApiError || error instanceof UnauthorizedError) {
            return error;
          }
          return new NetworkError({ cause: error });
        },
      });

    return {
      get: <T>(path: string, config?: Omit<RequestConfig, "body">) =>
        request<T>("GET", path, config),

      post: <T>(path: string, body?: unknown, config?: RequestConfig) =>
        request<T>("POST", path, { ...config, body }),

      put: <T>(path: string, body?: unknown, config?: RequestConfig) =>
        request<T>("PUT", path, { ...config, body }),

      patch: <T>(path: string, body?: unknown, config?: RequestConfig) =>
        request<T>("PATCH", path, { ...config, body }),

      delete: <T>(path: string, config?: Omit<RequestConfig, "body">) =>
        request<T>("DELETE", path, config),
    };
  }),
}) {}
```

### Session API

```ts
// shared/api/session.ts
import { Effect } from "effect";
import { ApiClient } from "./client";

export type Session = {
  readonly id: string;
  readonly userId: string;
  readonly expiresAt: Date;
};

export class SessionApi extends Effect.Service<SessionApi>()("@shared/api/session", {
  effect: Effect.gen(function* () {
    const client = yield* ApiClient;

    return {
      create: (userId: string) =>
        client.post<Session>("/sessions", { userId }),

      get: (sessionId: string) =>
        client.get<Session | null>(`/sessions/${sessionId}`),

      destroy: (sessionId: string) =>
        client.delete<void>(`/sessions/${sessionId}`),
    };
  }),
  dependencies: [ApiClient.Default],
}) {}
```

### API Index

```ts
// shared/api/index.ts
export { ApiClient } from "./client";
export { SessionApi, type Session } from "./session";
```

## Lib Segment

### Utilities

```ts
// shared/lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("ja-JP").format(num);
}

export function formatCompactNumber(num: number): string {
  return new Intl.NumberFormat("ja-JP", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);
}
```

### Error Classes

```ts
// shared/lib/errors.ts
import { Data } from "effect";

// Base validation error
export class ValidationError extends Data.TaggedError("ValidationError")<{
  readonly reason: string;
  readonly message?: string;
}> {}

// API errors
export class ApiError extends Data.TaggedError("ApiError")<{
  readonly status: number;
  readonly message: string;
}> {}

export class NetworkError extends Data.TaggedError("NetworkError")<{
  readonly cause?: unknown;
}> {}

export class UnauthorizedError extends Data.TaggedError("UnauthorizedError")<{}> {}

// Auth errors
export class AuthError extends Data.TaggedError("AuthError")<{
  readonly reason: "user_not_found" | "invalid_password" | "session_expired";
}> {}

// Union type for all errors
export type AppError =
  | ValidationError
  | ApiError
  | NetworkError
  | UnauthorizedError
  | AuthError;
```

### Date Utilities

```ts
// shared/lib/date.ts
import { Effect } from "effect";

export const formatDate = (date: Date): string =>
  new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);

export const formatDateTime = (date: Date): string =>
  new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);

export const parseISODate = (isoString: string): Effect.Effect<Date, ValidationError> =>
  Effect.try({
    try: () => {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) {
        throw new Error("Invalid date");
      }
      return date;
    },
    catch: () => new ValidationError({ reason: "invalid_date" }),
  });
```

### Auth Utilities

```ts
// shared/lib/auth.ts
import { redirect } from "react-router";
import { Effect } from "effect";
import { SessionApi, type Session } from "@/shared/api";
import { UnauthorizedError } from "./errors";

export const requireAuth = async (request: Request): Promise<User> => {
  const session = await getSession(request);
  if (!session) {
    throw redirect("/login");
  }
  return session.user;
};

export const getSession = async (request: Request): Promise<Session | null> => {
  const cookie = request.headers.get("Cookie");
  // Parse session from cookie...
  return null;
};
```

### Lib Index

```ts
// shared/lib/index.ts
export { cn, formatNumber, formatCompactNumber } from "./utils";
export { formatDate, formatDateTime, parseISODate } from "./date";
export { requireAuth, getSession } from "./auth";
export {
  ValidationError,
  ApiError,
  NetworkError,
  UnauthorizedError,
  AuthError,
  type AppError,
} from "./errors";
```

## Config Segment

### Environment Variables

```ts
// shared/config/env.ts
import { Effect, Config } from "effect";

export const AppConfig = {
  apiUrl: Config.string("API_URL").pipe(Config.withDefault("")),
  appName: Config.string("APP_NAME").pipe(Config.withDefault("<your-app>")),
  isDevelopment: Config.boolean("DEV").pipe(Config.withDefault(false)),
};

// Type-safe access
export const getConfig = <K extends keyof typeof AppConfig>(key: K) =>
  Effect.config(AppConfig[key]);
```

### Route Constants

```ts
// shared/config/routes.ts
export const ROUTES = {
  home: "/",
  login: "/login",
  signup: "/signup",
  dashboard: "/dashboard",
  videos: "/videos",
  videoDetail: (id: string) => `/videos/${id}`,
  accounts: "/accounts",
  reports: "/reports",
  settings: {
    root: "/settings",
    profile: "/settings/profile",
    security: "/settings/security",
    billing: "/settings/billing",
  },
} as const;
```

### Config Index

```ts
// shared/config/index.ts
export { AppConfig, getConfig } from "./env";
export { ROUTES } from "./routes";
```

## Types Segment

```ts
// shared/types/api.ts
export type ApiResponse<T> = {
  readonly data: T;
  readonly meta?: {
    readonly total?: number;
    readonly page?: number;
    readonly pageSize?: number;
  };
};

export type PaginatedResponse<T> = ApiResponse<T[]> & {
  readonly meta: {
    readonly total: number;
    readonly page: number;
    readonly pageSize: number;
    readonly totalPages: number;
  };
};

// shared/types/index.ts
export type { ApiResponse, PaginatedResponse } from "./api";
```

## Migration from application/

| application/          | shared/                  |
| --------------------- | ------------------------ |
| `components/ui/`      | `ui/`                    |
| `utils/`              | `lib/`                   |
| `utils/server/`       | `lib/` or `api/`         |
| `types/`              | `types/`                 |
| `gateway/`            | `api/`                   |
| `lib/`                | `lib/`                   |

## Key Principles

1. **No Business Logic**: Only generic, reusable code
2. **Highly Reusable**: Used by all other layers
3. **Stable**: Changes infrequently
4. **Well-Documented**: Types should be self-documenting
5. **Effect-First**: Use Effect for all I/O operations
