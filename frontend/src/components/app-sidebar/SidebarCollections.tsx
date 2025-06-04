import { CollectionLinkItem } from '@/components/app-sidebar/CollectionLinkItem';
import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu } from '@/components/ui/Sidebar';
import { collectionsQueryOptions } from '@/data/collections';
import { useAxios } from '@/integrations/axios';
import { useQuery } from '@tanstack/react-query';

export function SidebarCollections() {
  const axiosClient = useAxios();
  const { data: collections, isLoading } = useQuery(collectionsQueryOptions({ axiosClient }).all);

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Collections</SidebarGroupLabel>
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
