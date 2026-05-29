import type { ReactNode } from "react";

type WidgetCardProps = {
  title: string;
  children: ReactNode;
  dataLive: boolean;
};

export function WidgetCard({ title, children, dataLive }: WidgetCardProps) {
  return (
    <section
      className={dataLive ? "widget-card" : "widget-card widget-card--stale"}
      aria-label={title}
    >
      <header className="widget-card__header">{title}</header>
      {!dataLive ? (
        <p className="widget-card__stale-banner">Waiting for data…</p>
      ) : null}
      <div className="widget-card__body">{children}</div>
    </section>
  );
}
