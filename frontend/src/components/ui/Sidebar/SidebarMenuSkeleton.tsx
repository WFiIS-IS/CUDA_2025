import { type CSSProperties, type ComponentProps, useMemo } from 'react';

import { Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/styles';

export type SidebarMenuSkeletonProps = ComponentProps<'div'> & {
  showIcon?: boolean;
};

export function SidebarMenuSkeleton({ className, showIcon = false, ref, ...props }: SidebarMenuSkeletonProps) {
  // Random width between 50 to 90%.
  const width = useMemo(() => {
    return `${Math.floor(Math.random() * 40) + 50}%`;
  }, []);

  return (
    <div
      ref={ref}
      data-sidebar="menu-skeleton"
      className={cn('flex h-8 items-center gap-2 rounded-md px-2', className)}
      {...props}
    >
      {showIcon && <Skeleton className="size-4 rounded-md" data-sidebar="menu-skeleton-icon" />}
      <Skeleton
        className="h-4 max-w-[var(--skeleton-width)] flex-1"
        data-sidebar="menu-skeleton-text"
        style={
          {
            '--skeleton-width': width,
          } as CSSProperties
        }
      />
    </div>
  );
}
