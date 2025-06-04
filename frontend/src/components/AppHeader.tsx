import { useMatchRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { Separator } from '@/components/ui/Separator';
import { SidebarTrigger } from '@/components/ui/Sidebar';
import { cacheKeys } from '@/data/cache-keys';
import type { Bookmark, Collection } from '@/data/data-types';
import { useQueryClient } from '@tanstack/react-query';

export function AppHeader() {
  const matchRoute = useMatchRoute();
  const queryClient = useQueryClient();
  const ruleset = useMemo(
    () => [
      {
        cond: () => matchRoute({ to: '/', fuzzy: false }),
        getTitle: () => 'Home',
        getSubtitle: () => null,
      },
      {
        cond: () => matchRoute({ to: '/bookmarks' }),
        getTitle: () => 'All Bookmarks',
        getSubtitle: () => {
          const bookmarks = queryClient.getQueryData<Bookmark[]>(cacheKeys.bookmarks.all.queryKey)?.length ?? 0;
          return `${bookmarks} bookmark${bookmarks > 1 ? 's' : ''}`;
        },
      },
      {
        cond: () => matchRoute({ to: '/collection/$collectionId' }),
        getTitle: () => {
          const match = matchRoute({ to: '/collection/$collectionId' });
          if (!match) {
            throw new Error('Invariant matchRoute');
          }
          const { collectionId } = match;
          const collections = queryClient.getQueryData<Collection[]>(cacheKeys.collections.all.queryKey);
          const collection = collections?.find((c) => c.id === collectionId);
          return collection?.name ?? 'Collection';
        },
        getSubtitle: () => {
          const match = matchRoute({ to: '/collection/$collectionId' });
          if (!match) {
            throw new Error('Invariant matchRoute');
          }
          const { collectionId } = match;
          const collections = queryClient.getQueryData<Collection[]>(cacheKeys.collections.all.queryKey);
          const collection = collections?.find((c) => c.id === collectionId);
          const count = collection?.bookmarksCount ?? 0;
          return `${count} bookmark${count > 1 ? 's' : ''}`;
        },
      },
    ],
    [matchRoute, queryClient],
  );

  const rule = ruleset.find((rule) => rule.cond());
  if (!rule) {
    throw new Error('Invariant rule');
  }
  const title = rule.getTitle();
  const subtitle = rule.getSubtitle();

  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />
      <div className="flex flex-1 items-center justify-between">
        <div>
          <h2 className="font-semibold text-lg">{title}</h2>
          {subtitle ? <p className="text-muted-foreground text-sm">{subtitle}</p> : null}
        </div>
      </div>
    </header>
  );
}
