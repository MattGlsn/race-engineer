export type AppView = "dashboard" | "transcript";

const NAV_ITEMS: ReadonlyArray<{
  id: AppView;
  label: string;
}> = [
  { id: "dashboard", label: "Dashboard" },
  { id: "transcript", label: "Transcript" },
];

type SidebarNavProps = {
  activeId?: AppView;
  onNavigate?: (view: AppView) => void;
};

export function SidebarNav({ activeId = "dashboard", onNavigate }: SidebarNavProps) {
  return (
    <nav className="sidebar-nav" aria-label="Main navigation">
      <div className="sidebar-nav__brand">Race Engineer</div>
      <ul className="sidebar-nav__list">
        {NAV_ITEMS.map((item) => (
          <li key={item.id} className="sidebar-nav__item">
            <button
              type="button"
              className={
                item.id === activeId
                  ? "sidebar-nav__link sidebar-nav__link--active"
                  : "sidebar-nav__link"
              }
              aria-current={item.id === activeId ? "page" : undefined}
              onClick={() => onNavigate?.(item.id)}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
