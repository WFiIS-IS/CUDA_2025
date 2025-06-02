import type { ComponentProps } from 'react';

import { Sidebar, SidebarHeader, SidebarMenu } from '@/components/ui/Sidebar';

import { AppLogo } from './AppLogo';
import { SidebarContent } from './SidebarContent';

export function AppSidebar({ ...props }: ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <AppLogo />
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent />
    </Sidebar>
  );
}
