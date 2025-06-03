import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from '@tanstack/react-router';

import { createQueryClient } from '@/integrations/tanstack-query/client';

export function getTanStackQueryContext() {
  const queryClient = createQueryClient();

  return {
    queryClient,
  };
}

export type TanStackQueryProviderProps = {
  children: ReactNode;
  queryClient: QueryClient;
};

export function TanStackQueryProvider({ children, queryClient }: TanStackQueryProviderProps) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
