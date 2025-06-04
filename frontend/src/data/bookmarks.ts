import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllBookmarks } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';

export const bookmarksQueryOptions = ({ axiosClient }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.bookmarks.all,
    queryFn: () => fetchAllBookmarks({ axiosClient }),
  }),
});
