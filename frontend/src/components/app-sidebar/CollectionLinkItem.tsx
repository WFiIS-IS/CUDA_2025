import { Link, useMatchRoute } from '@tanstack/react-router';

import { Badge } from '@/components/ui/Badge';
import { SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from '@/components/ui/Sidebar';

import type { Collection } from '@/data/data-types';

export type CollectionLinkItemProps = {
  collection: Collection;
};

export function CollectionLinkItem({ collection }: CollectionLinkItemProps) {
  const matchRoute = useMatchRoute();
  const isActive = Boolean(matchRoute({ to: '/collection/$collectionId', params: { collectionId: collection.id } }));

  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild className="flex flex-row items-center justify-between" isActive={isActive}>
        <Link to="/collection/$collectionId" params={{ collectionId: collection.id }}>
          <span>{collection.name}</span>
          <Badge variant="outline">{collection.bookmarksCount}</Badge>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

function CollectionLinkItemSkeleton() {
  return (
    <SidebarMenuItem>
      <SidebarMenuSkeleton />
    </SidebarMenuItem>
  );
}

CollectionLinkItem.Skeleton = CollectionLinkItemSkeleton;
