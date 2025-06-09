import * as SelectPrimitive from '@radix-ui/react-select';
import type { ComponentProps } from 'react';

export type SelectValueProps = ComponentProps<typeof SelectPrimitive.Value>;

export function SelectValue({ ...props }: SelectValueProps) {
  return <SelectPrimitive.Value data-slot="select-value" {...props} />;
}
