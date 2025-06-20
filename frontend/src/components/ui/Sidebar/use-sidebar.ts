import { use } from 'react';

import { SidebarContext } from './sidebar-context';

export function useSidebar() {
  const context = use(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider.');
  }

  return context;
}
