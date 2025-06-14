import { ExternalLink, MoreHorizontal, Pencil, Trash } from 'lucide-react';
import { Suspense, useState } from 'react';

import { BookmarkCollectionName } from '@/components/bookmark/BookmarkCollectionName';
import { BookmarkTags } from '@/components/bookmark/BookmarkTags';
import { editBookmark } from '@/components/edit-drawer/drawer-store';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/AlertDialog';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/DropdownMenu';
import { Skeleton } from '@/components/ui/Skeleton';
import { useDeleteBookmark } from '@/data/bookmarks';
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
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { mutate: deleteBookmark } = useDeleteBookmark();

  return (
    <Card
      className="group h-[200px] cursor-pointer border border-transparent transition-all hover:scale-[1.03] hover:border-primary hover:shadow-md"
      onClick={(e) => {
        e.stopPropagation();
        window.open(url, '_blank');
      }}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <CardTitle className={cn('truncate font-medium text-sm', !title && 'text-muted-foreground')}>
              {title ?? formatUrl(url)}
            </CardTitle>
          </div>
          <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  window.open(url, '_blank');
                }}
              >
                <ExternalLink className="mr-2 h-4 w-4" />
                Open Link
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  editBookmark({
                    id,
                    url,
                    title,
                    description,
                    collectionId,
                  });
                }}
              >
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <AlertDialog
                open={isDeleteDialogOpen}
                onOpenChange={(open) => {
                  if (!open) {
                    setDropdownOpen(false);
                  }
                  setIsDeleteDialogOpen(open);
                }}
              >
                <AlertDialogTrigger asChild>
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                    }}
                    onSelect={(e) => {
                      e.preventDefault();
                    }}
                    className="text-destructive"
                  >
                    <Trash className="mr-2 h-4 w-4 text-destructive" />
                    Delete
                  </DropdownMenuItem>
                </AlertDialogTrigger>
                <AlertDialogContent onClick={(e) => e.stopPropagation()} onSelect={(e) => e.stopPropagation()}>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure you want to delete this bookmark?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete the bookmark.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteBookmark(id);
                      }}
                    >
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
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
