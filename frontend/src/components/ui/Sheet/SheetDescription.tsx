import * as SheetPrimitive from '@radix-ui/react-dialog';
import type { DialogDescriptionProps } from '@radix-ui/react-dialog';
import type { RefAttributes } from 'react';

import { cn } from '@/lib/styles';

export type SheetDescriptionProps = DialogDescriptionProps & RefAttributes<HTMLParagraphElement>;

export function SheetDescription({ className, ...props }: SheetDescriptionProps) {
  return <SheetPrimitive.Description className={cn('text-muted-foreground text-sm', className)} {...props} />;
}
