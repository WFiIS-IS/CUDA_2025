import { cn } from '@/lib/styles';
import type { ComponentProps } from 'react';

export type CommandShortcutProps = ComponentProps<'span'>;

export function CommandShortcut({ className, ...props }: CommandShortcutProps) {
  return (
    <span
      data-slot="command-shortcut"
      className={cn('ml-auto text-muted-foreground text-xs tracking-widest', className)}
      {...props}
    />
  );
}
