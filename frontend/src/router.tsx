import { createRouter as createTanStackRouter } from '@tanstack/react-router';

import { AxiosClientProvider, createAPIClient } from '@/integrations/axios';
import { TanStackQueryProvider, createQueryClient } from '@/integrations/tanstack-query';

import { routeTree } from './routeTree.gen';

export function createRouter() {
  const queryClient = createQueryClient();
  const apiClient = createAPIClient();

  return createTanStackRouter({
    routeTree,
    context: {
      apiClient,
      queryClient,
    },
    defaultPreload: 'intent',
    scrollRestoration: true,
    defaultStructuralSharing: true,
    defaultPreloadStaleTime: 0,
    Wrap: ({ children }) => (
      <TanStackQueryProvider queryClient={queryClient}>
        <AxiosClientProvider axiosClient={apiClient}>{children}</AxiosClientProvider>
      </TanStackQueryProvider>
    ),
  });
}

export type RouterContext = {
  apiClient: ReturnType<typeof createAPIClient>;
  queryClient: ReturnType<typeof createQueryClient>;
};
