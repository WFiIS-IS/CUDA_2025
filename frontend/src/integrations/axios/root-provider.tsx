import type { AxiosInstance } from 'axios';
import { type ReactNode, createContext, use } from 'react';

const ApiClientContext = createContext<AxiosInstance | null>(null);

export function useApiClient() {
  const axiosClient = use(ApiClientContext);

  if (!axiosClient) {
    throw new Error('Missing <AxiosClientProvider />');
  }

  return axiosClient;
}

export type AxiosClientProviderProps = {
  children: ReactNode;
  axiosClient: AxiosInstance;
};

export function AxiosClientProvider({ children, axiosClient }: AxiosClientProviderProps) {
  return <ApiClientContext value={axiosClient}>{children}</ApiClientContext>;
}
