import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type AlertDialogFooterProps = ComponentProps<'div'>;

export function AlertDialogFooter({ className, ...props }: AlertDialogFooterProps) {
  return (
    <div
      data-slot="alert-dialog-footer"
      className={cn('flex flex-col-reverse gap-2 sm:flex-row sm:justify-end', className)}
      {...props}
    />
  );
}
