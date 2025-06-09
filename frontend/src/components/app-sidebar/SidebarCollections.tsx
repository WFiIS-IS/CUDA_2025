import { useQuery } from '@tanstack/react-query';
import { FolderPlusIcon } from 'lucide-react';

import { CollectionLinkItem } from '@/components/app-sidebar/CollectionLinkItem';
import { CreateCollectionDialog } from '@/components/collection/CreateCollectionDialog';
import { Button } from '@/components/ui/Button';
import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu } from '@/components/ui/Sidebar';
import { Text } from '@/components/ui/Text';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/Tooltip';
import { collectionsQueryOptions } from '@/data/collections';
import { useApiClient } from '@/integrations/axios';

export function SidebarCollections() {
  const apiClient = useApiClient();
  const { data: collections, isLoading } = useQuery(collectionsQueryOptions({ apiClient }).all);

  return (
    <SidebarGroup>
      <div className="flex items-center justify-between">
        <SidebarGroupLabel>Collections</SidebarGroupLabel>
        <Tooltip>
          <CreateCollectionDialog>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon">
                <FolderPlusIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
          </CreateCollectionDialog>
          <TooltipContent>
            <Text>Create a new collection</Text>
          </TooltipContent>
        </Tooltip>
      </div>
      <SidebarGroupContent>
        <SidebarMenu>
          {isLoading
            ? Array.from({ length: 5 }).map((_, index) => <CollectionLinkItem.Skeleton key={index.toString()} />)
            : collections?.map((collection) => <CollectionLinkItem key={collection.id} collection={collection} />)}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
