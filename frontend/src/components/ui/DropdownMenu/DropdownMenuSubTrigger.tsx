import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { ChevronRightIcon } from 'lucide-react';
import type { ComponentProps } from 'react';

import { cn } from '@/lib/styles';

export type DropdownMenuSubTriggerProps = ComponentProps<typeof DropdownMenuPrimitive.SubTrigger> & {
  inset?: boolean;
};

export function DropdownMenuSubTrigger({ className, inset, children, ...props }: DropdownMenuSubTriggerProps) {
  return (
    <DropdownMenuPrimitive.SubTrigger
      data-slot="dropdown-menu-sub-trigger"
      data-inset={inset}
      className={cn(
        'flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-hidden focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[inset]:pl-8 data-[state=open]:text-accent-foreground',
        className,
      )}
      {...props}
    >
      {children}
      <ChevronRightIcon className="ml-auto size-4" />
    </DropdownMenuPrimitive.SubTrigger>
  );
}
