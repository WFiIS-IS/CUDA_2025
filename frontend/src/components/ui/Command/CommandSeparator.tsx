import { Command as CommandPrimitive } from 'cmdk';
import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type CommandSeparatorProps = ComponentProps<typeof CommandPrimitive.Separator>;

export function CommandSeparator({ className, ...props }: CommandSeparatorProps) {
  return (
    <CommandPrimitive.Separator
      data-slot="command-separator"
      className={cn('-mx-1 h-px bg-border', className)}
      {...props}
    />
  );
}
