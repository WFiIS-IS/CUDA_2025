import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type CardFooterProps = ComponentProps<'div'>;

export function CardFooter({ className, ...props }: CardFooterProps) {
  return (
    <div data-slot="card-footer" className={cn('flex items-center px-6 [.border-t]:pt-6', className)} {...props} />
  );
}
