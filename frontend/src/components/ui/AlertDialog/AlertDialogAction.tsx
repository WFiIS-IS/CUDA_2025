import * as AlertDialogPrimitive from '@radix-ui/react-alert-dialog';
import type { ComponentProps } from 'react';

import { buttonVariants } from '@/components/ui/Button';
import { cn } from '@/lib/styles';

export type AlertDialogActionProps = ComponentProps<typeof AlertDialogPrimitive.Action>;

export function AlertDialogAction({ className, ...props }: AlertDialogActionProps) {
  return <AlertDialogPrimitive.Action className={cn(buttonVariants(), className)} {...props} />;
}
