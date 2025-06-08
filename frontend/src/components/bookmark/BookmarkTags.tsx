import { Tag } from 'lucide-react';

import { Badge } from '@/components/ui/Badge';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import type { Bookmark } from '@/data/data-types';
import { useApiClient } from '@/integrations/axios';
import { useSuspenseQuery } from '@tanstack/react-query';

export type BookmarkTagsProps = {
  bookmarkId: Bookmark['id'];
};

export function BookmarkTags({ bookmarkId }: BookmarkTagsProps) {
  const apiClient = useApiClient();
  const { data: tags } = useSuspenseQuery(bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkId }).tags);

  return (
    <>
      {tags && tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              <Tag className="mr-1 h-3 w-3" />
              {tag}
            </Badge>
          ))}
          {tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{tags.length - 3}
            </Badge>
          )}
        </div>
      )}
    </>
  );
}
