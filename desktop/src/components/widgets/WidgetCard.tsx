import type { ReactNode } from "react";

type WidgetCardProps = {
  title: string;
  children: ReactNode;
};

export function WidgetCard({ title, children }: WidgetCardProps) {
  return (
    <section className="widget-card" aria-label={title}>
      <header className="widget-card__header">{title}</header>
      <div className="widget-card__body">{children}</div>
    </section>
  );
}
