import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllCollections, fetchCollectionById } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import type { Collection } from '@/data/data-types';

export const collectionsQueryOptions = ({ apiClient }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.collections.all,
    queryFn: () => fetchAllCollections({ apiClient }),
  }),
  byId: ({ collectionId }: { collectionId: Collection['id'] }) =>
    queryOptions({
      ...cacheKeys.collections.byId(collectionId),
      queryFn: () => fetchCollectionById({ apiClient, collectionId }),
    }),
});
