import { Command as CommandPrimitive } from 'cmdk';
import type { ComponentProps } from 'react';

export type CommandEmptyProps = ComponentProps<typeof CommandPrimitive.Empty>;

export function CommandEmpty({ ...props }: CommandEmptyProps) {
  return <CommandPrimitive.Empty data-slot="command-empty" className="py-6 text-center text-sm" {...props} />;
}
