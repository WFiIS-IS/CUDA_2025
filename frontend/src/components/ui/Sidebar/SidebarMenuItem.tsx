import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarMenuItemProps = ComponentProps<'li'>;

export function SidebarMenuItem({ className, ref, ...props }: SidebarMenuItemProps) {
  return <li ref={ref} data-sidebar="menu-item" className={cn('group/menu-item relative', className)} {...props} />;
}
