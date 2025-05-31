import type { ComponentProps } from 'react';

import { Separator } from '@/components/ui/Separator';
import { cn } from '@/lib/styles';

export type SidebarSeparatorProps = ComponentProps<typeof Separator>;

export function SidebarSeparator({ className, ref, ...props }: SidebarSeparatorProps) {
  return (
    <Separator
      ref={ref}
      data-sidebar="separator"
      className={cn('mx-2 w-auto bg-sidebar-border', className)}
      {...props}
    />
  );
}
