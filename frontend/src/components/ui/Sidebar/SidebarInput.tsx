import type { ComponentProps } from 'react';

import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/styles';

export type SidebarInputProps = ComponentProps<typeof Input>;

export function SidebarInput({ className, ref, ...props }: SidebarInputProps) {
  return (
    <Input
      ref={ref}
      data-sidebar="input"
      className={cn(
        'h-8 w-full bg-background shadow-none focus-visible:ring-2 focus-visible:ring-sidebar-ring',
        className,
      )}
      {...props}
    />
  );
}
