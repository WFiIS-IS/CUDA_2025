import type { ComponentProps } from 'react';

import { SidebarCollections } from '@/components/app-sidebar/SidebarCollections';
import { AllBookmarks } from '@/components/app-sidebar/menu-items/AllBookmarks';
import { UnsortedBookmarks } from '@/components/app-sidebar/menu-items/UnsortedBookmarks';
import { Sidebar, SidebarHeader, SidebarMenu } from '@/components/ui/Sidebar';

import { AppLogo } from './AppLogo';

export function AppSidebar({ ...props }: ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <AppLogo />
          <SidebarMenu>
            <AllBookmarks />
            <UnsortedBookmarks />
          </SidebarMenu>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarCollections />
    </Sidebar>
  );
}
