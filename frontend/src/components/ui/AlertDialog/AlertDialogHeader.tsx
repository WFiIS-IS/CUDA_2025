import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type AlertDialogHeaderProps = ComponentProps<'div'>;

export function AlertDialogHeader({ className, ...props }: AlertDialogHeaderProps) {
  return (
    <div
      data-slot="alert-dialog-header"
      className={cn('flex flex-col gap-2 text-center sm:text-left', className)}
      {...props}
    />
  );
}
