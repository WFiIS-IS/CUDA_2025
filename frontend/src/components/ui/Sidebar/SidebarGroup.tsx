import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarGroupProps = ComponentProps<'div'>;

export function SidebarGroup({ className, ref, ...props }: SidebarGroupProps) {
  return (
    <div
      ref={ref}
      data-sidebar="group"
      className={cn('relative flex w-full min-w-0 flex-col p-2', className)}
      {...props}
    />
  );
}
