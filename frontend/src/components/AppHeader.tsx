import { useLocation, useNavigate } from '@tanstack/react-router';
import { Search, X } from 'lucide-react';
import ms from 'ms';
import { useEffect, useState } from 'react';
import { useDebounce } from 'react-use';

import { CreateBookmarkDialog } from '@/components/bookmark/CreateBookmarkDialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Separator } from '@/components/ui/Separator';
import { SidebarTrigger } from '@/components/ui/Sidebar';

export type AppHeaderProps = {
  title?: string | null;
  subtitle?: string | null;
  collectionId?: string | null;
  enableSearch?: boolean;
};

export function AppHeader({ title, subtitle, collectionId, enableSearch = false }: AppHeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const pathname = useLocation({
    select: (location) => location.pathname,
  });
  const navigate = useNavigate();

  useDebounce(
    () => {
      if (searchQuery === '') {
        navigate({
          search: (prev) => {
            const { q, ...rest } = prev as { q?: string };
            return rest as never;
          },
          replace: true,
        });
        return;
      }

      navigate({
        search: (prev) => ({ ...prev, q: searchQuery }) as never,
        replace: true,
      });
    },
    ms('250ms'),
    [navigate, searchQuery],
  );

  useEffect(() => {
    if (pathname) {
      setSearchQuery('');
    }
  }, [pathname]);

  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />
      <div className="grid w-full grid-cols-3 items-center justify-between gap-3">
        <div className="grow-0">
          {title && <h2 className="font-semibold text-lg">{title}</h2>}
          {subtitle && <p className="text-muted-foreground text-sm">{subtitle}</p>}
        </div>
        {enableSearch && (
          <div className="relative">
            <Search className="-translate-y-1/2 absolute top-1/2 left-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search bookmarks..."
              className=" pr-9 pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                className="-translate-y-1/2 absolute top-1/2 right-1 h-7 w-7 p-0"
                onClick={() => setSearchQuery('')}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
        <div className="justify-self-end">
          <CreateBookmarkDialog collectionId={collectionId} />
        </div>
      </div>
    </header>
  );
}
