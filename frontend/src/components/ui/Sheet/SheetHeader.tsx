import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type SheetHeaderProps = ComponentProps<'div'>;

export function SheetHeader({ className, ...props }: SheetHeaderProps) {
  return <div className={cn('flex flex-col space-y-2 text-center sm:text-left', className)} {...props} />;
}
