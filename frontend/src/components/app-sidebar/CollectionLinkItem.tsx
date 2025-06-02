import type { Collection } from '@/data/types';

type NestedCollectionLinkItemProps = {
  collectionId: Collection['id'];
  collectionName: Collection['name'];
};

function NestedCollectionLinkItem({ collectionId, collectionName }: NestedCollectionLinkItemProps) {
  return null;
}

type FlatCollectionLinkItemProps = {
  collectionName: Collection['name'];
};

function FlatCollectionLinkItem({ collectionName }: FlatCollectionLinkItemProps) {
  return null;
}

export type CollectionLinkItemProps = {
  collection: Collection;
};

export function CollectionLinkItem({ collection }: CollectionLinkItemProps) {
  return null;
}
