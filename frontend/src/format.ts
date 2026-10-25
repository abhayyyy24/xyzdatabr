export const mw = (v: number | null | undefined) =>
  v == null ? "n/a" : `${Math.round(v).toLocaleString("en-GB")} MW`;

export const signedMw = (v: number | null | undefined) =>
  v == null ? "n/a" : `${v > 0 ? "+" : ""}${Math.round(v).toLocaleString("en-GB")} MW`;

export const pct = (v: number | null | undefined) =>
  v == null ? "n/a" : `${v.toFixed(1)}%`;

const ukTime = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Europe/London",
  hour: "2-digit",
  minute: "2-digit",
});
const ukDateTime = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Europe/London",
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

export const timeLabel = (iso: string) => ukTime.format(new Date(iso));
export const dateTimeLabel = (iso: string) => ukDateTime.format(new Date(iso));