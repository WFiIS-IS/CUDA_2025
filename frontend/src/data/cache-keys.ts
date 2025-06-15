import { createQueryKeyStore } from '@lukemorales/query-key-factory';

export const cacheKeys = createQueryKeyStore({
  bookmarks: {
    all: {
      queryKey: null,
      contextQueries: {
        search: (search?: string) => [{ search }],
      },
    },
    byCollectionId: (collectionId: string) => ({
      queryKey: [{ collectionId }],
      contextQueries: {
        search: (search?: string) => [{ search }],
      },
    }),
    unsorted: {
      queryKey: null,
      contextQueries: {
        search: (search?: string) => [{ search }],
      },
    },
    byId: (id: string) => ({
      queryKey: [{ id }],
      contextQueries: {
        tags: null,
        aiSuggestion: null,
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
