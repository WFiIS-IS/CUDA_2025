import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { useApiClient } from '@/integrations/axios';

export const Route = createFileRoute('/unsorted-bookmarks')({
  component: RouteComponent,
  loader: async ({ context: { apiClient, queryClient } }) => {
    await queryClient.ensureQueryData(bookmarksQueryOptions({ apiClient }).unsorted);
  },
});

function RouteComponent() {
  const apiClient = useApiClient();
  const { data: bookmarks } = useSuspenseQuery(bookmarksQueryOptions({ apiClient }).unsorted);

  const subtitle = useMemo(() => {
    const bookmarkCount = bookmarks.length;

    return `${bookmarkCount} bookmark${bookmarkCount === 1 ? '' : 's'}`;
  }, [bookmarks]);

  return (
    <PageWrapper header={<AppHeader title="Unsorted Bookmarks" subtitle={subtitle} />}>
      Hello "/unsorted-bookmarks"!
    </PageWrapper>
  );
}
