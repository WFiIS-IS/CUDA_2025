import { LayoutAddition as TanStackQueryLayout } from '@/integrations/tanstack-query';
import type { QueryClient } from '@tanstack/react-query';
import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

import { AppSidebar } from '@/components/app-sidebar';
import { SidebarProvider } from '@/components/ui/Sidebar';

type RouterContext = {
  queryClient: QueryClient;
};

export const Route = createRootRouteWithContext<RouterContext>()({
  component: () => (
    <SidebarProvider>
      <Outlet />
      <AppSidebar />
      <TanStackRouterDevtools />
      <TanStackQueryLayout />
    </SidebarProvider>
  ),
});
