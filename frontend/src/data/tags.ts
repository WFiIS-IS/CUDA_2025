import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllTags } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';

export const tagsQueryOptions = ({ apiClient, enabled = true }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.tags.all,
    queryFn: () => fetchAllTags({ apiClient }),
    enabled,
  }),
});
