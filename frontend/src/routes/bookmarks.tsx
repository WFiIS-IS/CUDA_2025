import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { useApiClient } from '@/integrations/axios';

export const Route = createFileRoute('/bookmarks')({
  component: BookmarksPage,
  loader: async ({ context: { queryClient, apiClient } }) => {
    await queryClient.ensureQueryData(bookmarksQueryOptions({ apiClient }).all);
  },
});

function BookmarksPage() {
  const apiClient = useApiClient();
  const { data: bookmarks } = useSuspenseQuery(bookmarksQueryOptions({ apiClient }).all);

  const subtitle = useMemo(() => {
    const bookmarkCount = bookmarks.length;

    return `${bookmarkCount} bookmark${bookmarkCount === 1 ? '' : 's'}`;
  }, [bookmarks]);

  return (
    <PageWrapper header={<AppHeader title="All Bookmarks" subtitle={subtitle} />}>Hello "/bookmarks/"!</PageWrapper>
  );
}
