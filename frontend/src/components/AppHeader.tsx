import { useMatchRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { Separator } from '@/components/ui/Separator';
import { SidebarTrigger } from '@/components/ui/Sidebar';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import { useAxios } from '@/integrations/axios';
import { useQuery } from '@tanstack/react-query';

export function AppHeader() {
  const matchRoute = useMatchRoute();
  const axiosClient = useAxios();
  const { data: collections } = useQuery(collectionsQueryOptions({ axiosClient }).all);
  const { data: bookmarks } = useQuery(bookmarksQueryOptions({ axiosClient }).all);

  const ruleset = useMemo(
    () => [
      {
        cond: () => matchRoute({ to: '/' }),
        getTitle: () => 'Home',
        getSubtitle: () => null,
      },
      {
        cond: () => matchRoute({ to: '/bookmarks' }),
        getTitle: () => 'All Bookmarks',
        getSubtitle: () => {
          const bookmarkCount = bookmarks?.length;

          if (bookmarkCount == null) {
            return null;
          }

          return `${bookmarkCount} bookmark${bookmarkCount > 1 ? 's' : ''}`;
        },
      },
      {
        cond: () => matchRoute({ to: '/collection/$collectionId' }),
        getTitle: ({
          collectionId,
        }: Exclude<ReturnType<typeof matchRoute<string, '/collection/$collectionId'>>, false>) => {
          const collection = collections?.find((c) => c.id === collectionId);
          return collection?.name ?? 'Collection';
        },
        getSubtitle: ({
          collectionId,
        }: Exclude<ReturnType<typeof matchRoute<string, '/collection/$collectionId'>>, false>) => {
          const collection = collections?.find((c) => c.id === collectionId);
          const count = collection?.bookmarksCount ?? 0;
          return `${count} bookmark${count > 1 ? 's' : ''}`;
        },
      } as const,
    ],
    [matchRoute, collections, bookmarks?.length],
  );

  const rule = ruleset.find((rule) => rule.cond());
  if (!rule) {
    throw new Error('Invariant rule');
  }
  // Following is correct, but TS is not able to infer the type of the rule.cond()
  const title = rule.getTitle(rule.cond() as never);
  const subtitle = rule.getSubtitle(rule.cond() as never);

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
