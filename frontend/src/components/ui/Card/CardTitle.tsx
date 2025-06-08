import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type CardTitleProps = ComponentProps<'div'>;

export function CardTitle({ className, ...props }: CardTitleProps) {
  return <div data-slot="card-title" className={cn('font-semibold leading-none', className)} {...props} />;
}
