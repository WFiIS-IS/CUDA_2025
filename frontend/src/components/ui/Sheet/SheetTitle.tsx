import * as SheetPrimitive from '@radix-ui/react-dialog';
import type { DialogTitleProps } from '@radix-ui/react-dialog';
import type { RefAttributes } from 'react';

import { cn } from '@/lib/styles';

export type SheetTitleProps = DialogTitleProps & RefAttributes<HTMLHeadingElement>;

export function SheetTitle({ className, ...props }: SheetTitleProps) {
  return <SheetPrimitive.Title className={cn('font-semibold text-foreground text-lg', className)} {...props} />;
}
