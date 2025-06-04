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

export async function fetchAllBookmarks({ axiosClient }: CommonQueryParams) {
  const response = await axiosClient.get('/api/bookmarks/');
  const validatedData = z.array(BookmarkSchema).parse(response.data);

  return validatedData;
}

export async function fetchAllCollections({ axiosClient }: CommonQueryParams) {
  const response = await axiosClient.get('/api/collections/');
  const validatedData = z.array(CollectionSchema).parse(response.data);

  return validatedData;
}

export async function createBookmark({ axiosClient, createData }: CommonQueryParams & { createData: BookmarkCreate }) {
  const response = await axiosClient.post('/api/bookmarks/', createData);
  const validatedData = BookmarkSchema.parse(response.data);

  return validatedData;
}

export async function createCollection({
  axiosClient,
  createData,
}: CommonQueryParams & { createData: CollectionCreate }) {
  const response = await axiosClient.post('/api/collections/', createData);
  const validatedData = CollectionSchema.parse(response.data);

  return validatedData;
}

export async function deleteBookmark({ axiosClient, bookmarkId }: CommonQueryParams & { bookmarkId: Bookmark['id'] }) {
  await axiosClient.delete(`bookmarks/${bookmarkId}/`);
}

export async function deleteCollection({
  axiosClient,
  collectionId,
}: CommonQueryParams & { collectionId: Collection['id'] }) {
  await axiosClient.delete(`/api/collections/${collectionId}/`);
}
