import * as SelectPrimitive from '@radix-ui/react-select';
import type { ComponentProps } from 'react';

export type SelectProps = ComponentProps<typeof SelectPrimitive.Root>;

export function Select({ ...props }: SelectProps) {
  return <SelectPrimitive.Root data-slot="select" {...props} />;
}
