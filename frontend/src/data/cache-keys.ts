import { createQueryKeyStore } from '@lukemorales/query-key-factory';

export const cacheKeys = createQueryKeyStore({
  bookmarks: {
    all: null,
    byCollectionId: (collectionId: string) => [{ collectionId }],
    unsorted: null,
    byId: (id: string) => ({
      queryKey: [{ id }],
      contextQueries: {
        tags: null,
      },
    }),
  },
  collections: {
    all: null,
    byId: (id: string) => [id],
  },
  tags: {
    all: null,
  },
});
