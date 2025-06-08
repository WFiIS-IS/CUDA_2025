import { createFileRoute } from '@tanstack/react-router';

import { AppHeader } from '@/components/AppHeader';
import { PageWrapper } from '@/components/PageWrapper';

export const Route = createFileRoute('/unsorted-bookmarks')({
  component: RouteComponent,
});

function RouteComponent() {
  return <PageWrapper header={<AppHeader title="Unsorted Bookmarks" />}>Hello "/unsorted-bookmarks"!</PageWrapper>;
}
