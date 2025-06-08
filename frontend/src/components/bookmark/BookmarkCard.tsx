import { ExternalLink, MoreHorizontal } from 'lucide-react';
import { Suspense } from 'react';

import { BookmarkCollectionName } from '@/components/bookmark/BookmarkCollectionName';
import { BookmarkTags } from '@/components/bookmark/BookmarkTags';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/DropdownMenu';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Bookmark } from '@/data/data-types';
import { cn } from '@/lib/styles';

function formatUrl(url: string) {
  const urlObj = new URL(url);
  return urlObj.hostname;
}

export type BookmarkCardProps = {
  id: string;
  url: string;
  title: string | null;
  description: string | null;
  collectionId: Bookmark['collectionId'];
};

export function BookmarkCard({ url, title, description, collectionId, id }: BookmarkCardProps) {
  return (
    <Card className="group h-[200px] cursor-pointer transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <CardTitle className={cn('truncate font-medium text-sm', !title && 'text-muted-foreground')}>
              {title ?? formatUrl(url)}
            </CardTitle>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <ExternalLink className="mr-2 h-4 w-4" />
                Open Link
              </DropdownMenuItem>
              <DropdownMenuItem>Edit</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {description && <CardDescription className="mt-1 line-clamp-2 text-xs">{description}</CardDescription>}
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-3">
          <Suspense fallback={<Skeleton className="h-4 w-18" />}>
            <BookmarkTags bookmarkId={id} />
          </Suspense>

          <div className="flex items-center justify-between text-muted-foreground text-xs">
            {collectionId && (
              <Suspense fallback={<Skeleton className="h-4 w-18" />}>
                <BookmarkCollectionName collectionId={collectionId} />
              </Suspense>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
