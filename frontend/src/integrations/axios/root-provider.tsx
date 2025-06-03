import type { AxiosInstance } from 'axios';
import { type ReactNode, createContext, use } from 'react';

import { createAPIClient } from './client';

const AxiosClientContext = createContext<AxiosInstance | null>(null);

export function useAxios() {
  const axiosClient = use(AxiosClientContext);

  if (!axiosClient) {
    throw new Error('Missing <AxiosClientProvider />');
  }

  return axiosClient;
}

export function getAxiosContext() {
  const axiosClient = createAPIClient();

  return {
    axiosClient,
  };
}

export type AxiosClientProviderProps = {
  children: ReactNode;
  axiosClient: AxiosInstance;
};

export function AxiosClientProvider({ children, axiosClient }: AxiosClientProviderProps) {
  return <AxiosClientContext value={axiosClient}>{children}</AxiosClientContext>;
}
