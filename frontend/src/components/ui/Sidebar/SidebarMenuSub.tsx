import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarMenuSubProps = ComponentProps<'ul'>;

export function SidebarMenuSub({ className, ref, ...props }: SidebarMenuSubProps) {
  return (
    <ul
      ref={ref}
      data-sidebar="menu-sub"
      className={cn(
        'mx-3.5 flex min-w-0 translate-x-px flex-col gap-1 border-sidebar-border border-l px-2.5 py-0.5',
        'group-data-[collapsible=icon]:hidden',
        className,
      )}
      {...props}
    />
  );
}
