import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SheetFooterProps = ComponentProps<'div'>;

export function SheetFooter({ className, ...props }: SheetFooterProps) {
  return <div className={cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', className)} {...props} />;
}
