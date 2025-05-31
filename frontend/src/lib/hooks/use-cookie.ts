import Cookies from 'js-cookie';
import ms from 'ms';
import { useCallback, useState } from 'react';

import { useInterval } from './use-interval';
import { useStatic } from './use-static';

const COOKIE_CHECK_INTERVAL = ms('1s');

function encodeCookieValue<T>(value: T | undefined): string | undefined {
  if (value === undefined) {
    return value as undefined;
  }

  return encodeURI(JSON.stringify(value));
}

function decodeCookieValue<T>(value?: string | undefined): T | undefined {
  if (value === undefined) {
    return value;
  }

  return JSON.parse(decodeURI(value));
}

export type UseCookieOptions = {
  noPooling?: boolean;
};

export function useCookie<T = string>(cookieName: string, { noPooling }: UseCookieOptions = {}) {
  const [cookie, setCookieValue] = useState<T | undefined>(() => decodeCookieValue<T>(Cookies.get(cookieName)));
  const poolingEnabled = useStatic(!noPooling);

  if (poolingEnabled) {
    const checkCookieInterval = useCallback(() => {
      const cookieValue = decodeCookieValue<T>(Cookies.get(cookieName));
      if (cookieValue !== cookie) {
        setCookieValue(() => cookieValue);
      }
    }, [cookieName, cookie]);

    useInterval(checkCookieInterval, COOKIE_CHECK_INTERVAL);
  }

  const setCookie = useCallback(
    (value: T, options?: Cookies.CookieAttributes) => {
      const encodedValue = encodeCookieValue(value);
      if (encodedValue) {
        Cookies.set(cookieName, encodedValue, options);
      } else {
        Cookies.remove(cookieName);
      }
      setCookieValue(() => value);
    },
    [cookieName],
  );

  const removeCookie = useCallback(() => {
    Cookies.remove(cookieName);
    setCookieValue(undefined);
  }, [cookieName]);

  return { cookie, setCookie, removeCookie } as const;
}
