import { createQueryKeyStore } from '@lukemorales/query-key-factory';

export const cacheKeys = createQueryKeyStore({
  bookmarks: {
    all: null,
    byCollectionId: (collectionId: string) => [{ collectionId }],
  },
  collections: {
    all: null,
    byId: (id: string) => [id],
  },
});
