import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SidebarGroupContentProps = ComponentProps<'div'>;

export function SidebarGroupContent({ className, ref, ...props }: SidebarGroupContentProps) {
  return <div ref={ref} data-sidebar="group-content" className={cn('w-full text-sm', className)} {...props} />;
}
