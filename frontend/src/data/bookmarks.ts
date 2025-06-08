import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllBookmarks, fetchBookmarksByCollectionId } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import type { Collection } from '@/data/data-types';

export const bookmarksQueryOptions = ({ apiClient }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.bookmarks.all,
    queryFn: () => fetchAllBookmarks({ apiClient }),
  }),
  byCollectionId: ({ collectionId }: { collectionId: Collection['id'] }) =>
    queryOptions({
      ...cacheKeys.bookmarks.byCollectionId(collectionId),
      queryFn: () => fetchBookmarksByCollectionId({ apiClient, collectionId }),
    }),
});
