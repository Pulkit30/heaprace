import "server-only";
import { cookies } from "next/headers";

export const TZ_COOKIE = "tz";

function isValidTimeZone(tz: string): boolean {
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: tz });
    return true;
  } catch {
    return false;
  }
}

/** The visitor's timezone from the cookie TimezoneSync sets, or UTC before it's known. */
export async function getUserTimeZone(): Promise<string> {
  const tz = (await cookies()).get(TZ_COOKIE)?.value;
  return tz && isValidTimeZone(tz) ? tz : "UTC";
}
