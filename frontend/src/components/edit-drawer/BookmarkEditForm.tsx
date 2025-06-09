import { useForm } from '@tanstack/react-form';
import { useSuspenseQueries } from '@tanstack/react-query';
import { CheckIcon, Tag } from 'lucide-react';
import { type FormEvent, useCallback } from 'react';
import z from 'zod/v4';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Combobox } from '@/components/ui/Combobox';
import { FieldInfo } from '@/components/ui/Form/FieldInfo';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Separator } from '@/components/ui/Separator';
import { Textarea } from '@/components/ui/Textarea';
import { bookmarksQueryOptions } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import type { Bookmark } from '@/data/data-types';
import { tagsQueryOptions } from '@/data/tags';
import { useApiClient } from '@/integrations/axios';
import { cn } from '@/lib/styles';

export type BookmarkEditFormProps = {
  bookmarkData: Bookmark;
};

const formSchema = z.object({
  url: z.url(),
  title: z.string().optional(),
  description: z.string().optional(),
  collectionId: z.string().optional(),
  tags: z.array(z.string()),
});

type FormType = z.infer<typeof formSchema>;

export function BookmarkEditForm({ bookmarkData }: BookmarkEditFormProps) {
  const apiClient = useApiClient();
  const { collections, tags, allTags } = useSuspenseQueries({
    queries: [
      collectionsQueryOptions({ apiClient }).all,
      bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkData.id }).tags,
      tagsQueryOptions({ apiClient }).all,
    ],
    combine: ([collectionResult, bookmarkResult, allTagsResult]) => {
      return {
        collections: collectionResult.data,
        tags: bookmarkResult.data,
        allTags: allTagsResult.data,
      };
    },
  });

  const form = useForm({
    defaultValues: {
      url: bookmarkData.url,
      title: bookmarkData.title ?? undefined,
      description: bookmarkData.description ?? undefined,
      collectionId: bookmarkData.collectionId ?? undefined,
      tags,
    } as FormType,
    onSubmit: (values) => {
      console.log(values);
    },
    validators: {
      onSubmit: formSchema,
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
    <form onSubmit={handleSubmit}>
      <div className="space-y-6 py-4">
        <form.Field name="title">
          {(field) => (
            <div className="space-y-2">
              <Label htmlFor={field.name}>Title</Label>
              <Input
                id={field.name}
                name={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Bookmark title"
              />
              <FieldInfo field={field} />
            </div>
          )}
        </form.Field>

        <form.Field name="url">
          {(field) => (
            <div className="space-y-2">
              <Label htmlFor={field.name}>URL</Label>
              <Input
                id={field.name}
                name={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
              />
            </div>
          )}
        </form.Field>

        <form.Field name="description">
          {(field) => (
            <div className="space-y-2">
              <Label htmlFor={field.name}>Description</Label>
              <Textarea
                id={field.name}
                name={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
              />
            </div>
          )}
        </form.Field>

        <form.Field name="collectionId">
          {(field) => (
            <div className="space-y-2">
              <Label>Collection</Label>
              <Combobox
                items={collections.map(({ id, name }) => ({
                  value: id,
                  label: name,
                }))}
                selected={field.state.value}
                onSelectedChange={(value) => field.handleChange(value)}
                placeholder="Select a collection"
                searchPlaceholder="Search collections..."
              />
            </div>
          )}
        </form.Field>

        <form.Field name="tags">
          {(field) => (
            <div className="space-y-2">
              <Label>Tags</Label>
              <span className="flex gap-2">
                <Combobox
                  items={allTags.map(({ tagName }) => ({
                    value: tagName,
                    label: tagName,
                  }))}
                  multiple
                  selected={field.state.value}
                  onSelectedChange={(value) => field.handleChange(value)}
                  placeholder="Select tags"
                  searchPlaceholder="Search tags..."
                  renderSelected={(selected) => {
                    const tags = selected.map(({ label }) => label).toSorted((a, b) => a.length - b.length);
                    return (
                      <div className="flex flex-wrap gap-1">
                        {tags.map((tag) => (
                          <Badge key={tag} variant="secondary" className="max-w-[160px] text-xs">
                            <Tag className="mr-1 h-3 w-3" />
                            <span className="truncate">{tag}</span>
                          </Badge>
                        ))}
                      </div>
                    );
                  }}
                  renderItem={({ item, isSelected }) => {
                    return (
                      <div className="flex w-full flex-nowrap gap-1">
                        <CheckIcon className={cn('mr-2 h-4 w-4', isSelected ? 'opacity-100' : 'opacity-0')} />
                        <Badge key={item.value} variant="secondary" className="flex shrink flex-nowrap text-xs">
                          <Tag className="mr-1 h-3 w-3" />
                          <span className="min-w-0 truncate">{item.label}</span>
                        </Badge>
                      </div>
                    );
                  }}
                  popoverActions={
                    <Button variant="secondary" className="w-full" size="sm">
                      New
                    </Button>
                  }
                />
              </span>
            </div>
          )}
        </form.Field>

        <Separator />

        <div className="space-y-2">
          <Label>Metadata</Label>
          <div className="space-y-1 text-muted-foreground text-sm">
            <p>ID: {bookmarkData.id}</p>
            <p>Collection ID: {bookmarkData.collectionId ?? '< Not Assigned >'}</p>
          </div>
        </div>
      </div>
    </form>
  );
}
