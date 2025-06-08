import { useSuspenseQueries } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import { useApiClient } from '@/integrations/axios';

export const Route = createFileRoute('/collection/$collectionId')({
  component: RouteComponent,
  loader: async ({ context: { queryClient, apiClient }, params: { collectionId } }) => {
    await Promise.all([
      queryClient.ensureQueryData(bookmarksQueryOptions({ apiClient }).byCollectionId({ collectionId })),
      queryClient.ensureQueryData(collectionsQueryOptions({ apiClient }).byId({ collectionId })),
    ]);
  },
});

function RouteComponent() {
  const apiClient = useApiClient();
  const { collectionId } = Route.useParams();
  const { bookmarks, collection } = useSuspenseQueries({
    queries: [
      bookmarksQueryOptions({ apiClient }).byCollectionId({ collectionId }),
      collectionsQueryOptions({ apiClient }).byId({ collectionId }),
    ],
    combine: (results) => {
      const [bookmarksResult, collectionResult] = results;

      return {
        bookmarks: bookmarksResult.data,
        collection: collectionResult.data,
      };
    },
  });

  const subtitle = useMemo(() => {
    const bookmarkCount = bookmarks.length;

    return `${bookmarkCount} bookmark${bookmarkCount === 1 ? '' : 's'}`;
  }, [bookmarks]);

  return (
    <PageWrapper header={<AppHeader title={collection.name} subtitle={subtitle} />}>
      Hello "/collection/$collectionId"!
    </PageWrapper>
  );
}
