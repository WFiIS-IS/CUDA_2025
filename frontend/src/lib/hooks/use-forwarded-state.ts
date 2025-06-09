import { type Dispatch, type SetStateAction, useCallback, useState } from 'react';

export type ForwardedState<T> = {
  state?: T;
  setState?: Dispatch<SetStateAction<T>> | ((value: T) => void);
  initialState: T;
};

export function useForwardedState<T>({ state, setState, initialState }: ForwardedState<T>) {
  const [localState, setLocalState] = useState<T>(initialState);
  const outState = state ?? localState;

  const outSetState = useCallback(
    (value: T) => {
      if (setState) {
        setState(value);
      }
      setLocalState(value);
    },
    [setState],
  );

  return [outState, outSetState] as const;
}
