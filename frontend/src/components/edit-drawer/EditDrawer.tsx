import { ExternalLink, Save } from 'lucide-react';
import { useId } from 'react';

import { BookmarkEditForm } from '@/components/edit-drawer/BookmarkEditForm';
import { Button } from '@/components/ui/Button';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/Sheet';

import { closeEditDrawer, useEditDrawerState } from './drawer-store';

export function EditDrawer() {
  const formId = useId();
  const { isOpen, initialData } = useEditDrawerState();

  if (!initialData) return null;

  return (
    <Sheet
      open={isOpen}
      onOpenChange={() => {
        closeEditDrawer();
      }}
    >
      <SheetContent className="flex flex-col ">
        <SheetHeader>
          <div className="flex items-center justify-between">
            <div>
              <SheetTitle>Edit Bookmark</SheetTitle>
              <SheetDescription>Make changes to your bookmark here.</SheetDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={() => window.open(initialData.url, '_blank')}>
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        <ScrollArea className="min-h-0 grow pr-4">
          <BookmarkEditForm bookmarkData={initialData} formId={formId} />
        </ScrollArea>

        <div className="flex justify-between border-t pt-4">
          <Button size="sm" form={formId} type="submit">
            <Save className="mr-2 h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
