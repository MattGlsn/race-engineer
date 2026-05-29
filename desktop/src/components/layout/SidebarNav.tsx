const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "transcript", label: "Transcript", disabled: true },
] as const;

type SidebarNavProps = {
  activeId?: string;
};

export function SidebarNav({ activeId = "dashboard" }: SidebarNavProps) {
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
              disabled={"disabled" in item && item.disabled}
              aria-current={item.id === activeId ? "page" : undefined}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
