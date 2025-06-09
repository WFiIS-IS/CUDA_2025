import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from '@tanstack/react-router';

export type TanStackQueryProviderProps = {
  children: ReactNode;
  queryClient: QueryClient;
};

export function TanStackQueryProvider({ children, queryClient }: TanStackQueryProviderProps) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
