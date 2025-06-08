import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type CardDescriptionProps = ComponentProps<'div'>;

export function CardDescription({ className, ...props }: CardDescriptionProps) {
  return <div data-slot="card-description" className={cn('text-muted-foreground text-sm', className)} {...props} />;
}
