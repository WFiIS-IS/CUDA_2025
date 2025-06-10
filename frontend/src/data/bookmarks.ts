import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import {
  createBookmark,
  deleteBookmark,
  fetchAllBookmarks,
  fetchBookmarkTags,
  fetchBookmarksByCollectionId,
} from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import { collectionsQueryOptions } from '@/data/collections';
import type { Bookmark, BookmarkCreate, Collection } from '@/data/data-types';
import { useApiClient } from '@/integrations/axios';

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

export function useCreateBookmark() {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (createData: BookmarkCreate) => {
      await createBookmark({ apiClient, createData });
    },
    onSettled: (_, __, { collectionId }) => {
      queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).all);
      if (collectionId) {
        queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).byCollectionId({ collectionId }));
      } else {
        queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).unsorted);
      }
      queryClient.invalidateQueries(collectionsQueryOptions({ apiClient }).all);
    },
  });
}

export function useDeleteBookmark() {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookmarkId: Bookmark['id']) => {
      await deleteBookmark({ bookmarkId, apiClient });
    },
    onSettled: (_, __) => {
      queryClient.invalidateQueries({
        queryKey: cacheKeys.collections._def,
      });
      queryClient.invalidateQueries({
        queryKey: cacheKeys.bookmarks._def,
      });
    },
  });
}
