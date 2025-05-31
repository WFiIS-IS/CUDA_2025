import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarHeaderProps = ComponentProps<'div'>;

export function SidebarHeader({ className, ref, ...props }: SidebarHeaderProps) {
  return <div ref={ref} data-sidebar="header" className={cn('flex flex-col gap-2 p-2', className)} {...props} />;
}
