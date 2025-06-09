import * as SelectPrimitive from '@radix-ui/react-select';
import type { ComponentProps } from 'react';

export type SelectGroupProps = ComponentProps<typeof SelectPrimitive.Group>;

export function SelectGroup({ ...props }: SelectGroupProps) {
  return <SelectPrimitive.Group data-slot="select-group" {...props} />;
}
