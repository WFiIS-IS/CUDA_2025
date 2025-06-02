import { SidebarMenuButton, SidebarMenuItem } from '@/components/ui/Sidebar';
import { Link } from '@tanstack/react-router';
import { PanelTopOpenIcon } from 'lucide-react';

export function UnsortedBookmarks() {
  return (
    <SidebarMenuItem className="flex flex-row items-center gap-2">
      <SidebarMenuButton asChild>
        <Link to="/bookmarks">
          <PanelTopOpenIcon size={18} />
          <span>Unsorted</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
