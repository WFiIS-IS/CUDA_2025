import { CreateBookmarkDialog } from '@/components/bookmark/CreateBookmarkDialog';
import { Separator } from '@/components/ui/Separator';
import { SidebarTrigger } from '@/components/ui/Sidebar';

export type AppHeaderProps = {
  title?: string | null;
  subtitle?: string | null;
  collectionId?: string | null;
};

export function AppHeader({ title, subtitle, collectionId }: AppHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />
      <div className="flex flex-1 items-center justify-between">
        <div>
          {title && <h2 className="font-semibold text-lg">{title}</h2>}
          {subtitle && <p className="text-muted-foreground text-sm">{subtitle}</p>}
        </div>
        <CreateBookmarkDialog collectionId={collectionId} />
      </div>
    </header>
  );
}
