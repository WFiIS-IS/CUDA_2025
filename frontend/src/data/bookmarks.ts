import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query';
import ms from 'ms';

import type { CommonQueryParams } from '@/data/api-types';
import {
  addTagToBookmark,
  createBookmark,
  deleteBookmark,
  fetchAllBookmarks,
  fetchBookmarkAISuggestion,
  fetchBookmarkTags,
  fetchBookmarksByCollectionId,
  removeTagFromBookmark,
  updateBookmark,
} from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import { collectionsQueryOptions } from '@/data/collections';
import type { Bookmark, BookmarkCreate, BookmarkUpdate, Collection } from '@/data/data-types';
import { tagsQueryOptions } from '@/data/tags';
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
    aiSuggestion: queryOptions({
      ...cacheKeys.bookmarks.byId(id)._ctx.aiSuggestion,
      queryFn: () => fetchBookmarkAISuggestion({ apiClient, bookmarkId: id }),
      enabled,
      refetchInterval: ms('1s'),
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

export type UpdateBookmarkParams = BookmarkUpdate & {
  tags?: {
    add?: string[];
    remove?: string[];
  };
};

export function useUpdateBookmark() {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id: bookmarkId, collectionId, tags, ...data }: UpdateBookmarkParams) => {
      const actions: Promise<void>[] = [];

      actions.push(updateBookmark({ apiClient, updateData: { id: bookmarkId, collectionId, ...data } }).then(() => {}));

      if (tags?.add) {
        actions.push(...tags.add.map((tag) => addTagToBookmark({ apiClient, bookmarkId, tag }).then(() => {})));
      }

      if (tags?.remove) {
        actions.push(...tags.remove.map((tag) => removeTagFromBookmark({ apiClient, bookmarkId, tag }).then(() => {})));
      }

      await Promise.all(actions);
    },
    onSettled: (_, __, { id, collectionId, tags }) => {
      if (collectionId) {
        queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).byCollectionId({ collectionId }));
      } else {
        queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).unsorted);
      }
      queryClient.invalidateQueries(collectionsQueryOptions({ apiClient }).all);
      queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).all);

      if (tags) {
        queryClient.invalidateQueries(tagsQueryOptions({ apiClient }).all);
        queryClient.invalidateQueries(bookmarksQueryOptions({ apiClient }).byId({ id }).tags);
      }
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
    onSettled: (_, __, bookmarkId) => {
      queryClient.cancelQueries(bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkId }).tags);
      queryClient.removeQueries(bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkId }).tags);

      queryClient.invalidateQueries({
        queryKey: cacheKeys.collections._def,
      });
      queryClient.invalidateQueries({
        queryKey: cacheKeys.bookmarks._def,
      });
      queryClient.invalidateQueries({
        queryKey: cacheKeys.tags._def,
      });
    },
  });
}
