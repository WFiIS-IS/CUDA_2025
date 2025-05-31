import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarMenuBadgeProps = ComponentProps<'div'>;

export function SidebarMenuBadge({ className, ref, ...props }: SidebarMenuBadgeProps) {
  return (
    <div
      ref={ref}
      data-sidebar="menu-badge"
      className={cn(
        'pointer-events-none absolute right-1 flex h-5 min-w-5 select-none items-center justify-center rounded-md px-1 font-medium text-sidebar-foreground text-xs tabular-nums',
        'peer-hover/menu-button:text-sidebar-accent-foreground peer-data-[active=true]/menu-button:text-sidebar-accent-foreground',
        'peer-data-[size=sm]/menu-button:top-1',
        'peer-data-[size=default]/menu-button:top-1.5',
        'peer-data-[size=lg]/menu-button:top-2.5',
        'group-data-[collapsible=icon]:hidden',
        className,
      )}
      {...props}
    />
  );
}
