import type { QueryClient } from '@tanstack/react-query';
import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import type { AxiosInstance } from 'axios';

import { AppHeader } from '@/components/AppHEader';
import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/Sidebar';
import { AxiosClientProvider } from '@/integrations/axios';
import { TanStackLayoutAddition, TanStackQueryProvider } from '@/integrations/tanstack-query';

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

type RouterContext = {
  queryClient: QueryClient;
  axiosClient: AxiosInstance;
};

function RootLayout() {
  const { queryClient, axiosClient } = Route.useRouteContext({
    select: (state) => ({
      queryClient: state.queryClient,
      axiosClient: state.axiosClient,
    }),
  });

  return (
    <TanStackQueryProvider queryClient={queryClient}>
      <AxiosClientProvider axiosClient={axiosClient}>
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset>
            <AppHeader />
            <main className="flex flex-1 flex-col gap-4 p-4">
              <SidebarInset>
                <Outlet />
              </SidebarInset>
            </main>
          </SidebarInset>
          <TanStackRouterDevtools />
          <TanStackLayoutAddition />
        </SidebarProvider>
      </AxiosClientProvider>
    </TanStackQueryProvider>
  );
}
