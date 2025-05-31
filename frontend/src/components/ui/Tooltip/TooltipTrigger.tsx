import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import type { RefAttributes } from 'react';

export type TooltipTriggerProps = TooltipPrimitive.TooltipTriggerProps & RefAttributes<HTMLButtonElement>;
export const TooltipTrigger = TooltipPrimitive.Trigger;
