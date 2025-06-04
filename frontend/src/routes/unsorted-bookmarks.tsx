import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/unsorted-bookmarks')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/unsorted-bookmarks"!</div>;
}
