import { useForm } from '@tanstack/react-form';
import type { AxiosError } from 'axios';
import { type FormEvent, type ReactNode, useCallback, useEffect, useState } from 'react';
import z from 'zod/v4';

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
import { useCreateTag } from '@/data/tags';

const formSchema = z.object({
  name: z.string().min(1),
});

export type NewTagDialogProps = {
  children: ReactNode;
};

export function NewTagDialog({ children }: NewTagDialogProps) {
  const [showDialog, setShowDialog] = useState(false);
  const { mutate: createTag } = useCreateTag({
    onSuccess: () => {
      setShowDialog(false);
    },
    onError: (error) => {
      const err = error as AxiosError;
      const responseData = err.response?.data as { detail: string };
      form.setErrorMap({
        onSubmit: {
          fields: {
            name: [{ message: responseData.detail }],
          },
        },
      });
    },
  });
  const form = useForm({
    defaultValues: {
      name: '',
    },
    validators: {
      onSubmit: formSchema,
    },
    onSubmit: ({ value }) => {
      createTag({ tag: value.name });
    },
  });

  useEffect(() => {
    if (showDialog) {
      form.reset();
    }
  }, [form.reset, showDialog]);

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
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create a new tag</DialogTitle>
          <DialogDescription>Create a new tag to organize your bookmarks</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <form.Field name="name">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name} data-error={!!field.state.meta.errors.length}>
                  Name
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
