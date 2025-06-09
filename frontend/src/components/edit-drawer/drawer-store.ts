import { useStore } from '@tanstack/react-store';
import { Store } from '@tanstack/store';

import type { Bookmark } from '@/data/data-types';

const editDrawerStore = new Store({
  isOpen: false,
  initialData: null as Bookmark | null,
});

export function editBookmark(bookmark: Bookmark) {
  editDrawerStore.setState(() => ({
    isOpen: true,
    initialData: bookmark,
  }));
}

export function closeEditDrawer() {
  editDrawerStore.setState(() => ({
    isOpen: false,
    initialData: null,
  }));
}

export function useEditDrawerState() {
  return useStore(editDrawerStore);
}
