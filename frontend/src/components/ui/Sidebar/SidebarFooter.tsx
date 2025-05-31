import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarFooterProps = ComponentProps<'div'>;

export function SidebarFooter({ className, ref, ...props }: SidebarFooterProps) {
  return <div ref={ref} data-sidebar="footer" className={cn('flex flex-col gap-2 p-2', className)} {...props} />;
}
