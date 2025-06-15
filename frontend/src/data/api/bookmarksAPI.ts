import { z } from 'zod/v4';

import type { CommonQueryParams } from '@/data/api-types';
import {
  type Bookmark,
  BookmarkAISuggestionSchema,
  type BookmarkCreate,
  BookmarkSchema,
  type BookmarkUpdate,
  type Collection,
  type CollectionCreate,
  CollectionSchema,
  type TagCreate,
  TagSchema,
} from '@/data/data-types';

export async function fetchAllBookmarks({
  apiClient,
  collectionId,
}: CommonQueryParams & { collectionId?: string | null }) {
  const qs = new URLSearchParams();
  if (collectionId !== undefined) {
    // Axios would just skip null values, so we need to stringify it
    qs.append('collectionId', JSON.stringify(collectionId));
  }

  const response = await apiClient.get(`/api/bookmarks/?${qs.toString()}`);
  const validatedData = z.array(BookmarkSchema).parse(response.data);

  return validatedData;
}

export async function fetchAllCollections({ apiClient }: CommonQueryParams) {
  const response = await apiClient.get('/api/collections/');
  const validatedData = z.array(CollectionSchema).parse(response.data);

  return validatedData;
}

export async function createBookmark({ apiClient, createData }: CommonQueryParams & { createData: BookmarkCreate }) {
  const response = await apiClient.post('/api/bookmarks/', createData);
  const validatedData = BookmarkSchema.parse(response.data);

  return validatedData;
}

export async function createCollection({
  apiClient,
  createData,
}: CommonQueryParams & { createData: CollectionCreate }) {
  const response = await apiClient.post('/api/collections/', createData);
  const validatedData = CollectionSchema.parse(response.data);

  return validatedData;
}

export async function deleteBookmark({ apiClient, bookmarkId }: CommonQueryParams & { bookmarkId: Bookmark['id'] }) {
  await apiClient.delete(`/api/bookmarks/${bookmarkId}/`);
}

export async function updateBookmark({ apiClient, updateData }: CommonQueryParams & { updateData: BookmarkUpdate }) {
  const response = await apiClient.put(`/api/bookmarks/${updateData.id}/`, updateData);
  const validatedData = BookmarkSchema.parse(response.data);

  return validatedData;
}

export async function deleteCollection({
  apiClient,
  collectionId,
}: CommonQueryParams & { collectionId: Collection['id'] }) {
  await apiClient.delete(`/api/collections/${collectionId}/`);
}

export async function fetchBookmarksByCollectionId({
  apiClient,
  collectionId,
}: CommonQueryParams & { collectionId: Collection['id'] }) {
  const response = await apiClient.get(`/api/collections/${collectionId}/bookmarks/`);
  const validatedData = z.array(BookmarkSchema).parse(response.data);

  return validatedData;
}

export async function fetchCollectionById({
  apiClient,
  collectionId,
}: CommonQueryParams & { collectionId: Collection['id'] }) {
  const response = await apiClient.get(`/api/collections/${collectionId}/`);
  const validatedData = CollectionSchema.parse(response.data);

  return validatedData;
}

export async function fetchBookmarkTags({ apiClient, bookmarkId }: CommonQueryParams & { bookmarkId: Bookmark['id'] }) {
  const response = await apiClient.get(`/api/bookmarks/${bookmarkId}/tags/`);
  const validatedData = z.array(z.string()).parse(response.data);

  return validatedData;
}

export async function addTagToBookmark({
  apiClient,
  bookmarkId,
  tag,
}: CommonQueryParams & { bookmarkId: Bookmark['id']; tag: string }) {
  const response = await apiClient.post(`/api/bookmarks/${bookmarkId}/tags/`, { tag });
  const validatedData = z.array(z.string()).parse(response.data);

  return validatedData;
}

export async function removeTagFromBookmark({
  apiClient,
  bookmarkId,
  tag,
}: CommonQueryParams & { bookmarkId: Bookmark['id']; tag: string }) {
  await apiClient.delete(`/api/bookmarks/${bookmarkId}/tags/${tag}/`);
}

export async function fetchAllTags({ apiClient }: CommonQueryParams) {
  const response = await apiClient.get('/api/tags/');
  const validatedData = z.array(TagSchema).parse(response.data);

  return validatedData;
}

export async function createTag({ apiClient, createData }: CommonQueryParams & { createData: TagCreate }) {
  const response = await apiClient.post('/api/tags/', createData);
  const validatedData = TagSchema.parse(response.data);

  return validatedData;
}

export async function fetchBookmarkAISuggestion({
  apiClient,
  bookmarkId,
}: CommonQueryParams & { bookmarkId: Bookmark['id'] }) {
  const response = await apiClient.get(`/api/bookmarks/${bookmarkId}/ai-suggestion/`);
  const validatedData = BookmarkAISuggestionSchema.parse(response.data);

  return validatedData;
}
