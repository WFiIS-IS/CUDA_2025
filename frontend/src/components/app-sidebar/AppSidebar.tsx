import { SidebarCollections } from '@/components/app-sidebar/SidebarCollections';
import { AllBookmarks } from '@/components/app-sidebar/menu-items/AllBookmarks';
import { UnsortedBookmarks } from '@/components/app-sidebar/menu-items/UnsortedBookmarks';
import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu } from '@/components/ui/Sidebar';

import { AppLogo } from './AppLogo';

export function AppSidebar() {
  return (
    <Sidebar variant="inset">
      <SidebarHeader>
        <SidebarMenu>
          <AppLogo />
          <SidebarMenu>
            <AllBookmarks />
            <UnsortedBookmarks />
          </SidebarMenu>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarCollections />
      </SidebarContent>
    </Sidebar>
  );
}
