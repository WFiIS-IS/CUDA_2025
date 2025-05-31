import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarContentProps = ComponentProps<'div'>;

export function SidebarContent({ className, ref, ...props }: SidebarContentProps) {
  return (
    <div
      ref={ref}
      data-sidebar="content"
      className={cn(
        'flex min-h-0 flex-1 flex-col gap-2 overflow-auto group-data-[collapsible=icon]:overflow-hidden',
        className,
      )}
      {...props}
    />
  );
}
