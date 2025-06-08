import { createQueryKeyStore } from '@lukemorales/query-key-factory';

export const cacheKeys = createQueryKeyStore({
  bookmarks: {
    all: null,
    byCollectionId: (collectionId: string) => [{ collectionId }],
    unsorted: null,
  },
  collections: {
    all: null,
    byId: (id: string) => [id],
  },
});
