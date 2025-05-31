import * as SheetPrimitive from '@radix-ui/react-dialog';
import type { DialogOverlayProps } from '@radix-ui/react-dialog';
import type { RefAttributes } from 'react';

import { cn } from '@/lib/styles';

export type SheetOverlayProps = DialogOverlayProps & RefAttributes<HTMLDivElement>;

export function SheetOverlay({ className, ...props }: SheetOverlayProps) {
  return (
    <SheetPrimitive.Overlay
      className={cn(
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80 data-[state=closed]:animate-out data-[state=open]:animate-in',
        className,
      )}
      {...props}
    />
  );
}
