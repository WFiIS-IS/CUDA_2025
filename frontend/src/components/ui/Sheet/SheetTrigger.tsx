import * as SheetPrimitive from '@radix-ui/react-dialog';
import type { DialogTriggerProps } from '@radix-ui/react-dialog';
import type { RefAttributes } from 'react';

export type SheetTriggerProps = DialogTriggerProps & RefAttributes<HTMLButtonElement>;
export const SheetTrigger = SheetPrimitive.Trigger;
