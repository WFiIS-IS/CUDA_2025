import { useSuspenseQueries } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';
import { BookmarkCard } from '@/components/bookmark/BookmarkCard';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import { useApiClient } from '@/integrations/axios';

export const Route = createFileRoute('/collection/$collectionId')({
  component: RouteComponent,
  loader: async ({ context: { queryClient, apiClient }, params: { collectionId } }) => {
    const bookmarks = await queryClient.fetchQuery(
      bookmarksQueryOptions({ apiClient }).byCollectionId({ collectionId }),
    );
    await Promise.all([
      ...bookmarks.map((bookmark) =>
        queryClient.ensureQueryData(bookmarksQueryOptions({ apiClient }).byId({ id: bookmark.id }).tags),
      ),
      ...bookmarks.map((bookmark) => {
        if (bookmark.collectionId) {
          return queryClient.ensureQueryData(
            collectionsQueryOptions({ apiClient }).byId({ collectionId: bookmark.collectionId }),
          );
        }

        return Promise.resolve();
      }),
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
      <ScrollArea className="flex-1">
        <div className="p-6">
          {bookmarks.length === 0 ? (
            <div className="flex h-64 items-center justify-center text-center">
              <div>
                <p className="font-medium text-lg text-muted-foreground">No bookmarks found</p>
                <p className="text-muted-foreground text-sm">Add some bookmarks to get started</p>
              </div>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {bookmarks.map((bookmark) => (
                <BookmarkCard key={bookmark.id} {...bookmark} />
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
    </PageWrapper>
  );
}
