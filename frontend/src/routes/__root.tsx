import type { QueryClient } from '@tanstack/react-query';
import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import type { AxiosInstance } from 'axios';

import { AppSidebar } from '@/components/app-sidebar';
import { SidebarProvider } from '@/components/ui/Sidebar';
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
          <Outlet />
          <AppSidebar />
          <TanStackRouterDevtools />
          <TanStackLayoutAddition />
        </SidebarProvider>
      </AxiosClientProvider>
    </TanStackQueryProvider>
  );
}
