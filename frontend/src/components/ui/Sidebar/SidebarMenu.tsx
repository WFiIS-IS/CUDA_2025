import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarMenuProps = ComponentProps<'ul'>;

export function SidebarMenu({ className, ref, ...props }: SidebarMenuProps) {
  return (
    <ul ref={ref} data-sidebar="menu" className={cn('flex w-full min-w-0 flex-col gap-1', className)} {...props} />
  );
}
