import { useSuspenseQuery } from '@tanstack/react-query';

import { collectionsQueryOptions } from '@/data/collections';
import type { Collection } from '@/data/data-types';
import { useApiClient } from '@/integrations/axios';

export type BookmarkCollectionNameProps = {
  collectionId: Collection['id'];
};

export function BookmarkCollectionName({ collectionId }: BookmarkCollectionNameProps) {
  const apiClient = useApiClient();
  const { data: collection } = useSuspenseQuery(collectionsQueryOptions({ apiClient }).byId({ collectionId }));

  return <span className="truncate">{collection.name}</span>;
}
