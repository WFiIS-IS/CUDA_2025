import { Link } from '@tanstack/react-router';

import { SidebarMenuButton, SidebarMenuItem } from '@/components/ui/Sidebar';
import { Text } from '@/components/ui/Text';

import AppIcon from './app-icon.svg?react';

export function AppLogo() {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild size="lg">
        <Link className="flex items-center justify-start rounded-md p-1" to="/">
          <span>
            <AppIcon width={50} />
          </span>
          <div className="flex flex-col">
            <Text variant="h4" className="select-none">
              {__PROJECT_NAME__}
            </Text>
            <span className="select-none text-muted-foreground">v{__PROJECT_VERSION__}</span>
          </div>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
