import { SidebarMenuButton, SidebarMenuItem } from '@/components/ui/Sidebar';
import { Link } from '@tanstack/react-router';

import { BookmarkIcon } from 'lucide-react';

export function AllBookmarks() {
  return (
    <SidebarMenuItem className="flex flex-row items-center gap-2">
      <SidebarMenuButton asChild>
        <Link to="/bookmarks">
          <BookmarkIcon size={18} />
          <span>All Bookmarks</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
