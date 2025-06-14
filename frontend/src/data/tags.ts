import { type MutationOptions, queryOptions, useMutation, useQueryClient } from '@tanstack/react-query';

import type { CommonQueryParams } from '@/data/api-types';
import { createTag, fetchAllTags } from '@/data/api/bookmarksAPI';
import { cacheKeys } from '@/data/cache-keys';
import type { Tag, TagCreate } from '@/data/data-types';
import { useApiClient } from '@/integrations/axios';

export const tagsQueryOptions = ({ apiClient, enabled = true }: CommonQueryParams) => ({
  all: queryOptions({
    ...cacheKeys.tags.all,
    queryFn: () => fetchAllTags({ apiClient }),
    enabled,
  }),
});

export type CreateTagMutation = Omit<MutationOptions<Tag, Error, TagCreate>, 'mutationFn'>;

export function useCreateTag({ onSettled, ...rest }: CreateTagMutation = {}) {
  const apiClient = useApiClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (createData: TagCreate) => createTag({ apiClient, createData }),
    onSettled: (data, error, variables, context) => {
      queryClient.invalidateQueries(tagsQueryOptions({ apiClient }).all);
      onSettled?.(data, error, variables, context);
    },
    ...rest,
  });
}
