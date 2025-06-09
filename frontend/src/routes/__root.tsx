import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

import { AppSidebar } from '@/components/app-sidebar';
import { EditDrawer } from '@/components/edit-drawer/EditDrawer';
import { SidebarProvider } from '@/components/ui/Sidebar';
import { TanStackLayoutAddition } from '@/integrations/tanstack-query';
import type { RouterContext } from '@/router';
import { Suspense } from 'react';

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <Outlet />
      <Suspense>
        <EditDrawer />
      </Suspense>
      <TanStackRouterDevtools />
      <TanStackLayoutAddition />
    </SidebarProvider>
  );
}
