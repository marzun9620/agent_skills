# Pages Layer

## Overview

Pages are **complete page compositions** that compose widgets, features, and entities to create full user-facing screens. Pages handle routing, data loading, and page-level state.

## Structure

```
pages/
└── {page-name}/
    ├── ui/                    # Page UI components
    │   ├── {Page}Page.tsx     # Main page component
    │   ├── {Page}Header.tsx   # Page-specific header
    │   └── index.ts
    ├── api/                   # Loaders and actions (optional)
    │   ├── loader.ts
    │   ├── action.ts
    │   └── index.ts
    ├── model/                 # Page-specific state (optional)
    │   └── index.ts
    └── index.ts               # Public API

routes/                        # React Router route files
└── {route}.tsx               # Route file that uses page
```

## Implementation Pattern

### 1. Page UI Component

```ts
// pages/login/ui/LoginPage.tsx
import { LoginForm } from "@/features/auth/login";
import { AppLogo } from "@/shared/ui";

export function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background">
      <div className="mb-8">
        <AppLogo size="lg" />
      </div>
      <LoginForm />
      <p className="mt-4 text-sm text-muted-foreground">
        Don't have an account?{" "}
        <a href="/signup" className="text-primary hover:underline">
          Sign up
        </a>
      </p>
    </div>
  );
}
```

### 2. Page with Multiple Features

```ts
// pages/dashboard/ui/DashboardPage.tsx
import { DashboardHeader } from "./DashboardHeader";
import { AccountSummaryWidget } from "@/widgets/account-summary";
import { VideoMetricsWidget } from "@/widgets/video-metrics";
import { RecentVideosWidget } from "@/widgets/recent-videos";

type DashboardPageProps = {
  readonly accountSummary: AccountSummary;
  readonly videoMetrics: VideoMetrics;
  readonly recentVideos: Video[];
};

export function DashboardPage({
  accountSummary,
  videoMetrics,
  recentVideos,
}: DashboardPageProps) {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto py-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AccountSummaryWidget data={accountSummary} />
          <VideoMetricsWidget data={videoMetrics} />
        </div>
        <RecentVideosWidget videos={recentVideos} />
      </main>
    </div>
  );
}
```

### 3. Page-Specific Header

```ts
// pages/dashboard/ui/DashboardHeader.tsx
import { useLoaderData } from "react-router";
import { UserAvatar } from "@/entities/user";
import { Button } from "@/shared/ui/button";

export function DashboardHeader() {
  const { user } = useLoaderData<{ user: User }>();

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto flex items-center justify-between h-16">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <div className="flex items-center gap-4">
          <Button variant="outline" asChild>
            <a href="/settings">Settings</a>
          </Button>
          <UserAvatar user={user} />
        </div>
      </div>
    </header>
  );
}
```

### 4. Page Public API

```ts
// pages/dashboard/index.ts
export { DashboardPage } from "./ui";
export type { DashboardPageProps } from "./ui";
```

## Route Integration

### Simple Route

```ts
// routes/login.tsx
import { LoginPage } from "@/pages/login";
import { LoginWorkflow } from "@/features/auth/login";
import { redirect } from "react-router";
import { Effect, Either } from "effect";
import type { Route } from "./+types/login";

export async function loader({ request }: Route.LoaderArgs) {
  // Redirect if already authenticated
  const session = await getSession(request);
  if (session) {
    return redirect("/dashboard");
  }
  return null;
}

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();

  const result = await Effect.runPromise(
    Effect.gen(function* () {
      const workflow = yield* LoginWorkflow;
      return yield* workflow.execute({
        email: formData.get("email") as string,
        password: formData.get("password") as string,
      });
    }).pipe(
      Effect.provide(LoginWorkflow.Default),
      Effect.either
    )
  );

  if (Either.isLeft(result)) {
    return { errors: { form: "Invalid credentials" } };
  }

  return redirect(result.right.redirectTo, {
    headers: {
      "Set-Cookie": await createSessionCookie(result.right.session),
    },
  });
}

export default function LoginRoute() {
  return <LoginPage />;
}
```

### Complex Route with Data Loading

```ts
// routes/dashboard.tsx
import { DashboardPage } from "@/pages/dashboard";
import { DashboardWorkflow } from "@/features/dashboard";
import { requireAuth } from "@/shared/lib/auth";
import { Effect } from "effect";
import type { Route } from "./+types/dashboard";

export async function loader({ request }: Route.LoaderArgs) {
  const user = await requireAuth(request);

  const data = await Effect.runPromise(
    Effect.gen(function* () {
      const workflow = yield* DashboardWorkflow;
      return yield* workflow.loadDashboardData(user.companyId);
    }).pipe(Effect.provide(DashboardWorkflow.Default))
  );

  return {
    user,
    ...data,
  };
}

export default function DashboardRoute() {
  const { user, accountSummary, videoMetrics, recentVideos } =
    useLoaderData<typeof loader>();

  return (
    <DashboardPage
      accountSummary={accountSummary}
      videoMetrics={videoMetrics}
      recentVideos={recentVideos}
    />
  );
}
```

## Layout Routes

```ts
// routes/_auth.tsx (Layout for auth pages)
import { Outlet } from "react-router";
import { AuthLayout } from "@/widgets/auth-layout";

export default function AuthLayoutRoute() {
  return (
    <AuthLayout>
      <Outlet />
    </AuthLayout>
  );
}

// routes/_auth.login.tsx
import { LoginPage } from "@/pages/login";

export default function LoginRoute() {
  return <LoginPage />;
}

// routes/_auth.signup.tsx
import { SignupPage } from "@/pages/signup";

export default function SignupRoute() {
  return <SignupPage />;
}
```

## Route Organization

```
routes/
├── _index.tsx              # Home page
├── _auth.tsx               # Auth layout
├── _auth.login.tsx         # Login page
├── _auth.signup.tsx        # Signup page
├── _user.tsx               # Authenticated layout
├── _user.dashboard.tsx     # Dashboard page
├── _user.videos.tsx        # Videos list
├── _user.videos.$id.tsx    # Video detail
├── _user.accounts.tsx      # Accounts list
├── _user.reports.tsx       # Reports list
├── _user.settings.tsx      # Settings layout
├── _user.settings.profile.tsx
└── _user.settings.security.tsx
```

## Migration from application/routes

### Original Structure

```
application/app/routes/
├── _auth+/
│   ├── login.tsx
│   └── signup.tsx
├── _user+/
│   ├── dashboard+/
│   ├── videos+/
│   └── settings+/
```

### Migrated Structure

```
your-app/
├── pages/
│   ├── login/
│   ├── signup/
│   ├── dashboard/
│   ├── videos/
│   └── settings/
├── routes/
│   ├── _auth.tsx
│   ├── _auth.login.tsx
│   ├── _user.tsx
│   ├── _user.dashboard.tsx
│   └── ...
```

## Key Principles

1. **Composition**: Pages compose widgets and features, not implement them
2. **Data Flow**: Data loading happens in routes, passed to pages as props
3. **No Business Logic**: Pages should not contain business logic
4. **Route Separation**: Keep route files thin, delegate to pages
5. **Props Over Hooks**: Prefer passing data as props over using hooks in pages

## Common Pages in <your-app>

| Page            | Route                    | Features Used                    |
| --------------- | ------------------------ | -------------------------------- |
| `login`         | `/login`                 | auth/login                       |
| `signup`        | `/signup`                | auth/signup                      |
| `dashboard`     | `/dashboard`             | dashboard/view                   |
| `videos`        | `/videos`                | video/search, video/filter       |
| `video-detail`  | `/videos/:id`            | video/details                    |
| `accounts`      | `/accounts`              | account/list, account/connect    |
| `reports`       | `/reports`               | report/list, report/create       |
| `settings`      | `/settings/*`            | settings/*                       |
