import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/collection/$collectionId')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/collection/$collectionId"!</div>;
}
