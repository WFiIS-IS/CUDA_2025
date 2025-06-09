import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type CardContentProps = ComponentProps<'div'>;

export function CardContent({ className, ...props }: CardContentProps) {
  return <div data-slot="card-content" className={cn('px-6', className)} {...props} />;
}
