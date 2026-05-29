import type { ReactNode } from "react";

import type { BridgeSocketState } from "../../hooks/useBridgeWebSocket";
import type { AppView } from "./SidebarNav";
import { SidebarNav } from "./SidebarNav";
import { StatusCards } from "./StatusCards";

type AppShellProps = {
  bridge: BridgeSocketState;
  activeView: AppView;
  onNavigate: (view: AppView) => void;
  children: ReactNode;
};

export function AppShell({ bridge, activeView, onNavigate, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <SidebarNav activeId={activeView} onNavigate={onNavigate} />
      </aside>
      <header className="app-shell__header">
        <StatusCards bridge={bridge} />
      </header>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}
