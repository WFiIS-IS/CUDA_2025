import { PanelLeft } from 'lucide-react';
import type { ComponentProps } from 'react';

import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/styles';

import { useSidebar } from './use-sidebar';

export type SidebarTriggerProps = ComponentProps<typeof Button>;

export function SidebarTrigger({ className, onClick, ref, ...props }: SidebarTriggerProps) {
  const { toggleSidebar } = useSidebar();

  return (
    <Button
      ref={ref}
      data-sidebar="trigger"
      variant="ghost"
      size="icon"
      className={cn('h-7 w-7', className)}
      onClick={(event) => {
        onClick?.(event);
        toggleSidebar();
      }}
      {...props}
    >
      <PanelLeft />
      <span className="sr-only">Toggle Sidebar</span>
    </Button>
  );
}
