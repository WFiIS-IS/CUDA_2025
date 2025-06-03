import { createQueryKeyStore } from '@lukemorales/query-key-factory';

export const cacheKeys = createQueryKeyStore({
  bookmarks: {
    all: null,
    byId: (id: string) => [id],
  },
  collections: {
    all: null,
    byId: (id: string) => [id],
  },
});
