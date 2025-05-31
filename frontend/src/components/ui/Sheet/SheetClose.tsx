import * as SheetPrimitive from '@radix-ui/react-dialog';
import type { DialogCloseProps } from '@radix-ui/react-dialog';
import type { RefAttributes } from 'react';

export type SheetCloseProps = DialogCloseProps & RefAttributes<HTMLButtonElement>;
export const SheetClose = SheetPrimitive.Close;
