import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { fallback, zodValidator } from '@tanstack/zod-adapter';
import { useMemo } from 'react';
import z from 'zod';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';
import { BookmarkCard } from '@/components/bookmark/BookmarkCard';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import { useApiClient } from '@/integrations/axios';

const unsortedBookmarksSearchSchema = z.object({
  q: fallback(z.string().optional(), undefined),
});

export const Route = createFileRoute('/unsorted-bookmarks')({
  component: RouteComponent,
  validateSearch: zodValidator(unsortedBookmarksSearchSchema),
  loaderDeps: ({ search }) => ({ search: search.q }),
  loader: async ({ context: { queryClient, apiClient }, deps: { search } }) => {
    const bookmarks = await queryClient.fetchQuery(bookmarksQueryOptions({ apiClient }).unsorted({ search }));
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
    ]);
  },
});

function RouteComponent() {
  const apiClient = useApiClient();
  const { search } = Route.useLoaderDeps();
  const { data: bookmarks } = useSuspenseQuery(bookmarksQueryOptions({ apiClient }).unsorted({ search }));

  const subtitle = useMemo(() => {
    const bookmarkCount = bookmarks.length;

    return `${bookmarkCount} bookmark${bookmarkCount === 1 ? '' : 's'}`;
  }, [bookmarks]);

  return (
    <PageWrapper header={<AppHeader title="Unsorted Bookmarks" subtitle={subtitle} enableSearch />}>
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
