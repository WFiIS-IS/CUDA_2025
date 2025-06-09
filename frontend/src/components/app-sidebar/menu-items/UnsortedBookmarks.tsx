import { Link, useMatchRoute } from '@tanstack/react-router';
import { PanelTopOpenIcon } from 'lucide-react';

import { SidebarMenuButton, SidebarMenuItem } from '@/components/ui/Sidebar';

export function UnsortedBookmarks() {
  const matchRoute = useMatchRoute();
  const isActive = Boolean(matchRoute({ to: '/unsorted-bookmarks' }));

  return (
    <SidebarMenuItem className="flex flex-row items-center gap-2">
      <SidebarMenuButton asChild isActive={isActive}>
        <Link to="/unsorted-bookmarks">
          <PanelTopOpenIcon size={18} />
          <span>Unsorted</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
