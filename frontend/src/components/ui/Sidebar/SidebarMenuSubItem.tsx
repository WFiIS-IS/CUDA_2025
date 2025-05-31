import type { ComponentProps } from 'react';

export type SidebarMenuSubItemProps = ComponentProps<'li'>;

export function SidebarMenuSubItem({ ref, ...props }: SidebarMenuSubItemProps) {
  return <li ref={ref} {...props} />;
}
