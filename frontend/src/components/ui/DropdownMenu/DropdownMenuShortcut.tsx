import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type DropdownMenuShortcutProps = ComponentProps<'span'>;

export function DropdownMenuShortcut({ className, ...props }: DropdownMenuShortcutProps) {
  return (
    <span
      data-slot="dropdown-menu-shortcut"
      className={cn('ml-auto text-muted-foreground text-xs tracking-widest', className)}
      {...props}
    />
  );
}
