import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { createCollection, deleteCollection, fetchAllCollections, fetchCollectionById } from '@/data/api/bookmarksAPI';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { cacheKeys } from '@/data/cache-keys';
import type { Collection, CollectionCreate } from '@/data/data-types';
import { useApiClient } from '@/integrations/axios';

export const collectionsQueryOptions = ({ apiClient, enabled = true }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.collections.all,
    queryFn: () => fetchAllCollections({ apiClient }),
    enabled,
  }),
  byId: ({ collectionId }: { collectionId: Collection['id'] }) =>
    queryOptions({
      ...cacheKeys.collections.byId(collectionId),
      queryFn: () => fetchCollectionById({ apiClient, collectionId }),
      enabled,
    }),
});

export function useCreateCollection() {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (createData: CollectionCreate) => {
      await createCollection({ apiClient, createData });
    },
    onSettled: () => {
      queryClient.invalidateQueries(collectionsQueryOptions({ apiClient }).all);
    },
  });
}

export function useDeleteCollection() {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (collectionId: Collection['id']) => {
      await deleteCollection({ apiClient, collectionId });
    },
    onSettled: () => {
      queryClient.invalidateQueries(collectionsQueryOptions({ apiClient }).all);
      queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).all);
    },
  });
}
