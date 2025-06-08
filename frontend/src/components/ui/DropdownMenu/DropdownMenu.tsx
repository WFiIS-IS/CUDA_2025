import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import type { ComponentProps } from 'react';

export type DropdownMenuProps = ComponentProps<typeof DropdownMenuPrimitive.Root>;

export function DropdownMenu({ ...props }: DropdownMenuProps) {
  return <DropdownMenuPrimitive.Root data-slot="dropdown-menu" {...props} />;
}
