import { z } from 'zod';

export const CollectionSchema = z.object({
  name: z.string(),
  id: z.string(),
});

export type Collection = z.infer<typeof CollectionSchema>;

export const BookmarkSchema = z.object({
  id: z.string(),
  url: z.string(),
  title: z.string().nullable(),
  description: z.string().nullable(),
  collectionId: z.string().nullable(),
});

export type Bookmark = z.infer<typeof BookmarkSchema>;

export type CollectionCreate = Pick<Collection, 'name'>;

export type BookmarkCreate = Pick<Bookmark, 'url' | 'title' | 'description' | 'collectionId'>;
