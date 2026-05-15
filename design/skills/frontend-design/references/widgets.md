# Widgets Layer

## Overview

Widgets are **large, self-contained UI blocks** that compose features and entities into reusable sections. Examples: Sidebar, Header, AccountSummaryCard, VideoMetricsChart.

Widgets are used across multiple pages but are too complex to be entities or features.

## Structure

```
widgets/
└── {widget-name}/
    ├── ui/                    # Widget UI components
    │   ├── {Widget}.tsx       # Main widget component
    │   ├── {Widget}Item.tsx   # Sub-components
    │   └── index.ts
    ├── model/                 # Widget-specific state (optional)
    │   └── index.ts
    └── index.ts               # Public API
```

## Implementation Pattern

### 1. Simple Widget

```ts
// widgets/app-header/ui/AppHeader.tsx
import { Link } from "react-router";
import { UserAvatar } from "@/entities/user";
import { Button } from "@/shared/ui/button";
import { AppLogo } from "@/shared/ui";
import type { User } from "@/entities/user";

type AppHeaderProps = {
  readonly user: User;
  readonly onLogout: () => void;
};

export function AppHeader({ user, onLogout }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2">
          <AppLogo />
          <span className="font-semibold"><your-app></span>
        </Link>

        <nav className="flex items-center gap-6">
          <Link to="/dashboard" className="text-sm hover:text-primary">
            Dashboard
          </Link>
          <Link to="/videos" className="text-sm hover:text-primary">
            Videos
          </Link>
          <Link to="/reports" className="text-sm hover:text-primary">
            Reports
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/settings">
              <SettingsIcon className="h-5 w-5" />
            </Link>
          </Button>
          <UserAvatar user={user} size="sm" />
          <Button variant="ghost" size="sm" onClick={onLogout}>
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
```

### 2. Composite Widget

```ts
// widgets/account-summary/ui/AccountSummaryWidget.tsx
import { TikTokAccountCard } from "@/entities/tiktok-account";
import { ConnectAccountButton } from "@/features/account/connect-tiktok";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import type { TikTokAccount } from "@/entities/tiktok-account";

type AccountSummaryWidgetProps = {
  readonly accounts: TikTokAccount[];
  readonly onConnect: () => void;
  readonly onDisconnect: (accountId: string) => void;
};

export function AccountSummaryWidget({
  accounts,
  onConnect,
  onDisconnect,
}: AccountSummaryWidgetProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Connected Accounts</CardTitle>
        <ConnectAccountButton onClick={onConnect} />
      </CardHeader>
      <CardContent>
        {accounts.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No accounts connected yet.
          </p>
        ) : (
          <div className="space-y-3">
            {accounts.map((account) => (
              <TikTokAccountCard
                key={account.id}
                account={account}
                onDisconnect={() => onDisconnect(account.id)}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

### 3. Widget with Internal State

```ts
// widgets/video-metrics/ui/VideoMetricsWidget.tsx
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { MetricsChart } from "./MetricsChart";
import type { VideoMetrics } from "@/entities/video";

type VideoMetricsWidgetProps = {
  readonly metrics: VideoMetrics;
};

export function VideoMetricsWidget({ metrics }: VideoMetricsWidgetProps) {
  const [period, setPeriod] = useState<"7d" | "30d" | "90d">("7d");

  const filteredData = filterByPeriod(metrics.data, period);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Video Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={period} onValueChange={(v) => setPeriod(v as typeof period)}>
          <TabsList>
            <TabsTrigger value="7d">7 Days</TabsTrigger>
            <TabsTrigger value="30d">30 Days</TabsTrigger>
            <TabsTrigger value="90d">90 Days</TabsTrigger>
          </TabsList>
          <TabsContent value={period}>
            <MetricsChart data={filteredData} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
```

### 4. Layout Widget

```ts
// widgets/app-sidebar/ui/AppSidebar.tsx
import { Link, useLocation } from "react-router";
import { cn } from "@/shared/lib/utils";
import {
  LayoutDashboard,
  Video,
  Users,
  FileText,
  Settings,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/videos", icon: Video, label: "Videos" },
  { href: "/accounts", icon: Users, label: "Accounts" },
  { href: "/reports", icon: FileText, label: "Reports" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r bg-card min-h-screen">
      <nav className="p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              location.pathname.startsWith(item.href)
                ? "bg-primary text-primary-foreground"
                : "hover:bg-accent"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

### 5. Widget Public API

```ts
// widgets/account-summary/index.ts
export { AccountSummaryWidget } from "./ui";
export type { AccountSummaryWidgetProps } from "./ui";

// widgets/app-sidebar/index.ts
export { AppSidebar } from "./ui";
```

## Widget vs Feature vs Entity

| Aspect        | Entity                   | Feature                  | Widget                   |
| ------------- | ------------------------ | ------------------------ | ------------------------ |
| Purpose       | Business data            | User action              | UI composition           |
| Contains      | Types, validators, CRUD  | Workflow, forms          | Composed UI blocks       |
| Reusability   | High (across features)   | Medium (specific action) | High (across pages)      |
| Examples      | UserCard, VideoThumbnail | LoginForm, SearchBar     | Header, Sidebar, Chart   |

## Widget Patterns

### Presentational Widget

No internal state, pure rendering:

```ts
export function StatCard({ title, value, change }: StatCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={cn("text-xs", change >= 0 ? "text-green-500" : "text-red-500")}>
          {change >= 0 ? "+" : ""}{change}%
        </p>
      </CardContent>
    </Card>
  );
}
```

### Container Widget

Manages local state and child coordination:

```ts
export function DataTableWidget<T>({ data, columns, onRowClick }: Props<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [filtering, setFiltering] = useState("");

  // Table logic...

  return (
    <div>
      <Input value={filtering} onChange={...} placeholder="Filter..." />
      <Table>...</Table>
    </div>
  );
}
```

## Key Principles

1. **Self-Contained**: Widgets should work with minimal props
2. **Composable**: Widgets compose features and entities
3. **No Business Logic**: Keep business logic in features
4. **Reusable**: Design for use across multiple pages
5. **Page-Agnostic**: Widgets don't know which page they're on

## Common Widgets in <your-app>

| Widget              | Description                           | Composes                    |
| ------------------- | ------------------------------------- | --------------------------- |
| `app-header`        | Main navigation header                | entities/user               |
| `app-sidebar`       | Navigation sidebar                    | -                           |
| `auth-layout`       | Layout for auth pages                 | shared/ui                   |
| `user-layout`       | Layout for authenticated pages        | app-header, app-sidebar     |
| `account-summary`   | TikTok accounts overview              | entities/tiktok-account     |
| `video-metrics`     | Video performance chart               | entities/video              |
| `recent-videos`     | Recent videos list                    | entities/video              |
| `report-preview`    | Report preview card                   | entities/report             |
