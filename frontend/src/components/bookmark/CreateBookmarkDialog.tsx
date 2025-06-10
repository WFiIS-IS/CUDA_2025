import { useForm } from '@tanstack/react-form';
import { BookmarkPlus } from 'lucide-react';
import { type FormEvent, useCallback, useState } from 'react';
import { z } from 'zod/v4';

import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/Dialog';
import { FieldInfo } from '@/components/ui/Form/FieldInfo';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Spinner } from '@/components/ui/Spinner';
import { useCreateBookmark } from '@/data/bookmarks';

const formSchema = z.object({
  url: z.url(),
});

export type CreateBookmarkDialogProps = {
  collectionId?: string | null;
};

export function CreateBookmarkDialog({ collectionId }: CreateBookmarkDialogProps) {
  const [showDialog, setShowDialog] = useState(false);
  const { mutateAsync: createBookmark } = useCreateBookmark();
  const form = useForm({
    defaultValues: {
      url: '',
    },
    validators: {
      onSubmit: formSchema,
    },
    onSubmit: async ({ value }) => {
      await createBookmark({
        collectionId: collectionId ?? null,
        title: null,
        description: null,
        ...value,
      });
      setShowDialog(false);
    },
  });

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      e.stopPropagation();
      form.handleSubmit();
    },
    [form.handleSubmit],
  );

  return (
    <Dialog open={showDialog} onOpenChange={setShowDialog}>
      <DialogTrigger asChild>
        <Button className="gap-2">
          <BookmarkPlus className="h-4 w-4" />
          Add Bookmark
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <DialogHeader>
            <DialogTitle>Create a new bookmark</DialogTitle>
            <DialogDescription>Create a new bookmark to save to your collection</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4">
            <form.Field name="url">
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name} data-error={!!field.state.meta.errors.length}>
                    URL
                  </Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    data-error={!!field.state.meta.errors.length}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  <FieldInfo field={field} />
                </div>
              )}
            </form.Field>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
              {([canSubmit, isSubmitting]) => (
                <Button type="submit" disabled={!canSubmit}>
                  {isSubmitting ? <Spinner size="small" /> : 'Create'}
                </Button>
              )}
            </form.Subscribe>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
