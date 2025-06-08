import { AppHeader } from '@/components/AppHeader';
import { SidebarInset } from '@/components/ui/Sidebar';
import type { ReactNode } from 'react';

export type PageWrapperProps = {
  children: ReactNode;
  header?: ReactNode;
};

export function PageWrapper({ children, header }: PageWrapperProps) {
  return (
    <SidebarInset>
      {header ? header : <AppHeader />}
      <main className="flex flex-1 flex-col gap-4 p-4">{children}</main>
    </SidebarInset>
  );
}
