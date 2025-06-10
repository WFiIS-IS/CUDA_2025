import * as AlertDialogPrimitive from '@radix-ui/react-alert-dialog';
import type { ComponentProps } from 'react';

import { buttonVariants } from '@/components/ui/Button';
import { cn } from '@/lib/styles';

export type AlertDialogCancelProps = ComponentProps<typeof AlertDialogPrimitive.Cancel>;

export function AlertDialogCancel({ className, ...props }: AlertDialogCancelProps) {
  return <AlertDialogPrimitive.Cancel className={cn(buttonVariants({ variant: 'outline' }), className)} {...props} />;
}
