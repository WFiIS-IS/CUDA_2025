import { Link, useMatchRoute } from '@tanstack/react-router';

import { SidebarMenuButton, SidebarMenuItem } from '@/components/ui/Sidebar';

import { BookmarkIcon } from 'lucide-react';

export function AllBookmarks() {
  const matchRoute = useMatchRoute();
  const isActive = Boolean(matchRoute({ to: '/bookmarks' }));

  return (
    <SidebarMenuItem className="flex flex-row items-center gap-2">
      <SidebarMenuButton asChild isActive={isActive}>
        <Link to="/bookmarks">
          <BookmarkIcon size={18} />
          <span>All Bookmarks</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
