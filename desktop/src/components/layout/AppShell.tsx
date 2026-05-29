import type { ReactNode } from "react";

import type { BridgeSocketState } from "../../hooks/useBridgeWebSocket";
import { SidebarNav } from "./SidebarNav";
import { StatusCards } from "./StatusCards";

type AppShellProps = {
  bridge: BridgeSocketState;
  children: ReactNode;
};

export function AppShell({ bridge, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <SidebarNav />
      </aside>
      <header className="app-shell__header">
        <StatusCards bridge={bridge} />
      </header>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}
