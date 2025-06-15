import { type AnyFieldApi, useForm } from '@tanstack/react-form';
import { useSuspenseQueries } from '@tanstack/react-query';
import { CheckIcon, Sparkles, Tag } from 'lucide-react';
import { type FormEvent, useCallback } from 'react';
import z from 'zod/v4';

import { NewTagDialog } from '@/components/edit-drawer/NewTagDialog';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Combobox } from '@/components/ui/Combobox';
import { FieldInfo } from '@/components/ui/Form/FieldInfo';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Separator } from '@/components/ui/Separator';
import { Textarea } from '@/components/ui/Textarea';
import { bookmarksQueryOptions, useUpdateBookmark } from '@/data/bookmarks';
import { collectionsQueryOptions } from '@/data/collections';
import type { Bookmark } from '@/data/data-types';
import { tagsQueryOptions, useCreateTag } from '@/data/tags';
import { useApiClient } from '@/integrations/axios';
import { cn } from '@/lib/styles';

export type BookmarkEditFormProps = {
  bookmarkData: Bookmark;
  formId?: string;
};

const formSchema = z.object({
  url: z.url(),
  title: z.string().optional(),
  description: z.string().optional(),
  collectionId: z.string().optional(),
  tags: z.array(z.string()),
});

type FormType = z.infer<typeof formSchema>;

export function BookmarkEditForm({ bookmarkData, formId }: BookmarkEditFormProps) {
  const apiClient = useApiClient();
  const { collections, tags, allTags } = useSuspenseQueries({
    queries: [
      collectionsQueryOptions({ apiClient }).all,
      bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkData.id }).tags,
      tagsQueryOptions({ apiClient }).all,
      bookmarksQueryOptions({ apiClient }).byId({ id: bookmarkData.id }).aiSuggestion,
    ],
    combine: ([collectionResult, bookmarkResult, allTagsResult, aiSuggestionResult]) => {
      return {
        collections: collectionResult.data,
        tags: bookmarkResult.data,
        allTags: allTagsResult.data,
        aiSuggestion: aiSuggestionResult.data,
      };
    },
  });
  const { mutate: updateBookmark } = useUpdateBookmark();
  const { mutate: createTag } = useCreateTag();

  const form = useForm({
    defaultValues: {
      url: bookmarkData.url,
      title: bookmarkData.title ?? undefined,
      description: bookmarkData.description ?? undefined,
      collectionId: bookmarkData.collectionId ?? undefined,
      tags,
    } as FormType,
    onSubmit: ({ value }) => {
      const removedTags = tags.filter((tag) => !value.tags.includes(tag));
      const addedTags = value.tags.filter((tag) => !tags.includes(tag));

      updateBookmark({
        id: bookmarkData.id,
        collectionId: value.collectionId ?? null,
        title: value.title ?? null,
        description: value.description ?? null,
        url: value.url,
        tags: {
          add: addedTags,
          remove: removedTags,
        },
      });
    },

    validators: {
      onSubmit: formSchema,
    },
  });

  const aiSuggestion = {
    title: 'AI Suggestion',
    description: 'AI Suggestion',
    tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10'],
    collectionId: null,
  };

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      e.stopPropagation();
      form.handleSubmit();
    },
    [form.handleSubmit],
  );

  const handleAiTagSuggestionClick = useCallback(
    (field: AnyFieldApi, tag: string) => {
      const tagAlreadyExists = allTags.some(({ tagName }) => tagName === tag);
      if (!tagAlreadyExists) {
        createTag({ tag });
      }
      field.handleChange([...field.state.value, tag]);
    },
    [allTags, createTag],
  );

  return (
    <form onSubmit={handleSubmit} id={formId} className="w-full max-w-full">
      <div className="flex w-full min-w-0 max-w-full grow-0 flex-col space-y-6 py-4">
        <form.Field name="title">
          {(field) => (
            <div className="min-w-0 space-y-2">
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
              {aiSuggestion?.title && !field.state.meta.isDirty && (
                <div className="flexflex-wrap mt-1 items-center gap-2">
                  <Badge
                    variant="outline"
                    className="flex w-full flex-start cursor-pointer whitespace-pre-line break-words border-2 border-primary bg-primary/10 px-3 py-2 font-semibold text-primary shadow-sm transition-colors duration-150 hover:bg-primary/20 [&>svg]:size-5"
                    onClick={() => field.handleChange(aiSuggestion.title)}
                  >
                    <Sparkles className="mr-1 text-primary " />
                    {aiSuggestion.title}
                  </Badge>
                </div>
              )}
            </div>
          )}
        </form.Field>

        <form.Field name="url">
          {(field) => (
            <div className="min-w-0 space-y-2">
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
          {(field) => {
            return (
              <div className="min-w-0 space-y-2">
                <Label htmlFor={field.name}>Description</Label>
                <Textarea
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
                {aiSuggestion?.description && !field.state.meta.isDirty && (
                  <div className="relative mt-1 flex flex-wrap items-center gap-2">
                    <span className="absolute top-2 left-3 flex items-center [&>svg]:size-5" title="AI Suggestion">
                      <Sparkles className="text-primary" />
                    </span>
                    <Badge
                      variant="outline"
                      className="w-full cursor-pointer whitespace-pre-line break-words border-2 border-primary bg-primary/10 px-3 py-2 pt-8 font-semibold text-primary shadow-sm transition-colors duration-150 hover:bg-primary/20"
                      onClick={() => field.handleChange(aiSuggestion.description)}
                    >
                      <span className="w-full">{aiSuggestion.description}</span>
                    </Badge>
                  </div>
                )}
              </div>
            );
          }}
        </form.Field>

        <form.Field name="collectionId">
          {(field) => (
            <div className="min-w-0 max-w-full space-y-2">
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
          {(field) => {
            const aiTagsToSuggest = !aiSuggestion.tags
              ? null
              : aiSuggestion.tags.filter((tagName) => !field.state.value.includes(tagName));

            return (
              <div className="min-w-0 space-y-2">
                <div className="relative min-w-0 space-y-2">
                  <Label>Tags</Label>
                  <span className="flex min-w-0 gap-2">
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
                        <NewTagDialog>
                          <Button variant="secondary" className="w-full" size="sm">
                            New
                          </Button>
                        </NewTagDialog>
                      }
                    />
                  </span>
                  {aiTagsToSuggest && Array.isArray(aiTagsToSuggest) && aiTagsToSuggest.length > 0 && (
                    <div className="relative mt-1">
                      <div className="flex items-center gap-2 rounded-md border border-primary/30 bg-primary/5 p-2 [&>svg]:size-5">
                        <Sparkles className="h-4 w-4 text-primary" />
                        <span className="grid grow place-items-center content-center items-center justify-center gap-2 [grid-template-columns:repeat(auto-fit,minmax(60px,1fr))]">
                          {aiTagsToSuggest.map((tag: string) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="cursor-pointer border-2 border-primary bg-primary/10 p-1 font-semibold text-primary shadow-sm transition-colors duration-150 hover:bg-primary/20"
                              onClick={() => {
                                handleAiTagSuggestionClick(field, tag);
                              }}
                            >
                              <Tag className="mr-1 h-3 w-3" />
                              <span className="truncate">{tag}</span>
                            </Badge>
                          ))}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          }}
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
