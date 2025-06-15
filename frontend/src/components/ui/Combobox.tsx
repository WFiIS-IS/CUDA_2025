import Fuse from 'fuse.js';
import { CheckIcon, ChevronsUpDownIcon } from 'lucide-react';
import { type JSX, useCallback, useEffect, useMemo, useState } from 'react';

import { Button } from '@/components/ui/Button';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/Command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { Separator } from '@/components/ui/Separator';
import { useForwardedState } from '@/lib/hooks/use-forwarded-state';
import { cn } from '@/lib/styles';

export type ComboboxItem = {
  value: string;
  label: string;
};

export type ComboboxProps = {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  defaultOpen?: boolean;
  items: ComboboxItem[];
  placeholder?: string;
  searchPlaceholder?: string;
  popoverActions?: JSX.Element;
  renderSelected?: (selected: Array<ComboboxItem>) => JSX.Element;
  renderItem?: (props: { item: ComboboxItem; isSelected: boolean }) => JSX.Element;
} & (
  | {
      selected: string | undefined;
      onSelectedChange: (value: string | undefined) => void;
      multiple?: false;
    }
  | {
      selected: string[];
      onSelectedChange: (value: string[]) => void;
      multiple: true;
    }
);

export function Combobox({
  open,
  onOpenChange,
  defaultOpen = false,
  multiple,
  selected: selectedProp,
  items,
  placeholder = 'Select an item',
  searchPlaceholder = 'Search...',
  onSelectedChange,
  renderSelected = DefaultSelectRenderer,
  renderItem = DefaultItemRenderer,
  popoverActions,
}: ComboboxProps) {
  const [search, setSearch] = useState('');
  const [localOpen, setLocalOpen] = useForwardedState({
    state: open,
    setState: onOpenChange,
    initialState: open ?? defaultOpen,
  });

  const fuse = useMemo(() => new Fuse(items, { keys: ['label'], threshold: 0.4 }), [items]);

  useEffect(() => {
    if (localOpen) {
      setSearch('');
    }
  }, [localOpen]);

  const selected = useMemo(() => {
    if (multiple) {
      return selectedProp;
    }
    const value = selectedProp;
    if (!value) {
      return [];
    }
    return [value];
  }, [selectedProp, multiple]);

  const selectedOptions = useMemo(() => items.filter((item) => selected.includes(item.value)), [items, selected]);

  const handleSelect = useCallback(
    (selectedId: string) => {
      const wasSelected = selected.includes(selectedId);
      let newSelected: string[];

      if (wasSelected) {
        newSelected = selected.filter((item) => item !== selectedId);
      } else {
        const item = items.find((item) => item.value === selectedId);

        if (!item) {
          throw new Error(`Item with value ${selectedId} not found`);
        }

        if (multiple) {
          newSelected = [...selected, item.value];
        } else {
          newSelected = [item.value];
        }
      }

      if (multiple) {
        onSelectedChange(newSelected);
      } else {
        onSelectedChange(newSelected.at(0) ?? undefined);
        setLocalOpen(false);
      }
    },
    [items, multiple, onSelectedChange, selected, setLocalOpen],
  );
  const filteredItems = useMemo(
    () => (search.trim() === '' ? items : fuse.search(search).map(({ item }) => item)),
    [search, items, fuse],
  );

  return (
    <Popover open={localOpen} onOpenChange={setLocalOpen} modal>
      <PopoverTrigger asChild>
        {/* biome-ignore lint/a11y/useSemanticElements: <explanation> */}
        <Button
          role="combobox"
          variant="outline"
          aria-expanded={open}
          size="content"
          className="w-full justify-between"
        >
          <span className="truncate">{selectedOptions.length > 0 ? renderSelected(selectedOptions) : placeholder}</span>
          <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command shouldFilter={false}>
          <CommandInput placeholder={searchPlaceholder} value={search} onValueChange={setSearch} />
          <CommandList>
            <CommandEmpty>No framework found.</CommandEmpty>
            <CommandGroup>
              <ScrollArea>
                {filteredItems.map((item) => (
                  <CommandItem key={item.label} value={item.value} onSelect={handleSelect}>
                    {renderItem({ item, isSelected: selected.includes(item.value) })}
                  </CommandItem>
                ))}
              </ScrollArea>
            </CommandGroup>
          </CommandList>
        </Command>
        {popoverActions && (
          <>
            <Separator />
            <div className="flex flex-col p-2">{popoverActions}</div>
          </>
        )}
      </PopoverContent>
    </Popover>
  );
}

function DefaultSelectRenderer(selected: ComboboxItem[]) {
  return <>{selected.map((item) => item.label).join(', ')}</>;
}

function DefaultItemRenderer({ item, isSelected }: { item: ComboboxItem; isSelected: boolean }) {
  return (
    <>
      <CheckIcon className={cn('mr-2 h-4 w-4', isSelected ? 'opacity-100' : 'opacity-0')} />
      {item.label}
    </>
  );
}
