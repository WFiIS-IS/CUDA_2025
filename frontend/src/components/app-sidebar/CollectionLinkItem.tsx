import { Link, useMatchRoute, useNavigate } from '@tanstack/react-router';
import { MoreHorizontal, Trash2 } from 'lucide-react';
import { useState } from 'react';

import { Badge } from '@/components/ui/Badge';
import { SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from '@/components/ui/Sidebar';

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
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/DropdownMenu';
import { useDeleteCollection } from '@/data/collections';
import type { Collection } from '@/data/data-types';
import { cn } from '@/lib/styles';

export type CollectionLinkItemProps = {
  collection: Collection;
};

export function CollectionLinkItem({ collection }: CollectionLinkItemProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const { mutate: deleteCollection } = useDeleteCollection();
  const navigate = useNavigate();
  const matchRoute = useMatchRoute();

  const isActive = Boolean(matchRoute({ to: '/collection/$collectionId', params: { collectionId: collection.id } }));

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        asChild
        className="group/collection-item flex flex-row items-center justify-between gap-2"
        isActive={isActive}
      >
        <Link to="/collection/$collectionId" params={{ collectionId: collection.id }}>
          <span className="shrink truncate">{collection.name}</span>
          <span className="flex shrink-0 items-center justify-between gap-2">
            <Badge variant="outline">{collection.bookmarksCount}</Badge>
            <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn('hidden h-8 p-0 group-hover/collection-item:block', isDropdownOpen && 'block')}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <AlertDialog
                  open={isDeleteDialogOpen}
                  onOpenChange={(open) => {
                    if (!open) {
                      setIsDropdownOpen(false);
                    }
                    setIsDeleteDialogOpen(open);
                  }}
                >
                  <AlertDialogTrigger asChild>
                    <DropdownMenuItem className="text-destructive" onSelect={(e) => e.preventDefault()}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                      Delete
                    </DropdownMenuItem>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you sure you want to delete this collection?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete the collection and all its bookmarks.
                      </AlertDialogDescription>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={(e) => {
                            e.stopPropagation();
                            if (isActive) {
                              navigate({ to: '/bookmarks', replace: true });
                            }
                            deleteCollection(collection.id);
                          }}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogHeader>
                  </AlertDialogContent>
                </AlertDialog>
              </DropdownMenuContent>
            </DropdownMenu>
          </span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

function CollectionLinkItemSkeleton() {
  return (
    <SidebarMenuItem>
      <SidebarMenuSkeleton />
    </SidebarMenuItem>
  );
}

CollectionLinkItem.Skeleton = CollectionLinkItemSkeleton;
