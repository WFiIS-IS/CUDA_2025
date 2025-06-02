import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/bookmarks/')({
  component: BookmarksPage,
});

function BookmarksPage() {
  return <div>Hello "/bookmarks/"!</div>;
}
