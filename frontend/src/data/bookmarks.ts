import { queryOptions } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { fetchAllBookmarks, fetchBookmarkTags, fetchBookmarksByCollectionId } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import type { Bookmark, Collection } from '@/data/data-types';

export const bookmarksQueryOptions = ({ apiClient, enabled = true }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.bookmarks.all,
    queryFn: () => fetchAllBookmarks({ apiClient }),
    enabled,
  }),
  unsorted: queryOptions({
    ...cacheKeys.bookmarks.unsorted,
    queryFn: () => fetchAllBookmarks({ apiClient, collectionId: null }),
    enabled,
  }),
  byCollectionId: ({ collectionId }: { collectionId: Collection['id'] }) =>
    queryOptions({
      ...cacheKeys.bookmarks.byCollectionId(collectionId),
      queryFn: () => fetchBookmarksByCollectionId({ apiClient, collectionId }),
      enabled,
    }),
  byId: ({ id }: { id: Bookmark['id'] }) => ({
    tags: queryOptions({
      ...cacheKeys.bookmarks.byId(id)._ctx.tags,
      queryFn: () => fetchBookmarkTags({ apiClient, bookmarkId: id }),
      enabled,
    }),
  }),
});
