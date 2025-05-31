import { useRef } from 'react';

export function useStatic<T>(value: T) {
  const ref = useRef<T>(value);
  return ref.current;
}
