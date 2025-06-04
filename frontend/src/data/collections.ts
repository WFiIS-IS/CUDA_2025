import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllCollections } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';

export const collectionsQueryOptions = ({ axiosClient }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.collections.all,
    queryFn: () => fetchAllCollections({ axiosClient }),
  }),
});
