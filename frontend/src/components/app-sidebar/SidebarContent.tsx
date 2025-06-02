import { SidebarContent as SidebarContentComponent, SidebarGroup, SidebarMenu } from '@/components/ui/Sidebar';

export function SidebarContent() {
  return (
    <SidebarContentComponent>
      <SidebarGroup>
        <SidebarMenu>{null}</SidebarMenu>
      </SidebarGroup>
    </SidebarContentComponent>
  );
}
