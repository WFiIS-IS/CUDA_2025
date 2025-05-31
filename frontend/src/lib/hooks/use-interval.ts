import { useEffect, useRef, useState } from 'react';

export function useInterval(callback: () => void, delay: number | undefined) {
  const savedCallback = useRef<typeof callback>(null);
  const [clearIntervalCallback, setClearIntervalCallback] = useState<VoidFunction>(() => () => {});

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    const handler = () => savedCallback.current?.();
    if (delay !== null) {
      const id = setInterval(handler, delay);
      setClearIntervalCallback(() => () => {
        clearInterval(id);
      });

      return () => clearInterval(id);
    }
  }, [delay]);

  return clearIntervalCallback;
}
