import { type VariantProps, cva } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';

import { cn } from '@/lib/styles';
import type { ReactNode } from 'react';

export const spinnerVariants = cva('animate-spin flex-col items-center justify-center text-primary', {
  variants: {
    show: {
      true: 'flex',
      false: 'hidden',
    },
    size: {
      small: 'size-6',
      medium: 'size-8',
      large: 'size-12',
    },
  },
  defaultVariants: {
    show: true,
  },
});

export const loaderVariants = cva('animate-spin text-primary', {
  variants: {
    size: {
      small: 'size-6',
      medium: 'size-8',
      large: 'size-12',
    },
  },
  defaultVariants: {
    size: 'medium',
  },
});

export type SpinnerProps = {
  className?: string;
  children?: ReactNode;
} & VariantProps<typeof spinnerVariants> &
  VariantProps<typeof loaderVariants>;

export function Spinner({ size, show, children, className }: SpinnerProps) {
  return (
    <span className={spinnerVariants({ show })}>
      <Loader2 className={cn(loaderVariants({ size }), className)} />
      {children}
    </span>
  );
}
