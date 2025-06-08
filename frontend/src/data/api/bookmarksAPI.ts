import { z } from 'zod';

import type { CommonQueryParams } from '@/data/api-types';
import {
  type Bookmark,
  type BookmarkCreate,
  BookmarkSchema,
  type Collection,
  type CollectionCreate,
  CollectionSchema,
} from '@/data/data-types';

export async function fetchAllBookmarks({ apiClient }: CommonQueryParams) {
  const response = await apiClient.get('/api/bookmarks/');
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
  await apiClient.delete(`bookmarks/${bookmarkId}/`);
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
