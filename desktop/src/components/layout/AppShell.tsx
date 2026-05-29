import type { ReactNode } from "react";

import type { PersonalityMode } from "../../types/personalityMode";
import type { BridgeSocketState } from "../../hooks/useBridgeWebSocket";
import { EngineerToneControl } from "../settings/EngineerToneControl";
import type { AppView } from "./SidebarNav";
import { SidebarNav } from "./SidebarNav";
import { StatusCards } from "./StatusCards";

type AppShellProps = {
  bridge: BridgeSocketState;
  activeView: AppView;
  onNavigate: (view: AppView) => void;
  personalityMode: PersonalityMode;
  onSelectPersonalityMode: (mode: PersonalityMode) => void;
  personalitySyncError: string | null;
  children: ReactNode;
};

export function AppShell({
  bridge,
  activeView,
  onNavigate,
  personalityMode,
  onSelectPersonalityMode,
  personalitySyncError,
  children,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <SidebarNav
          activeId={activeView}
          onNavigate={onNavigate}
          footer={
            <EngineerToneControl
              mode={personalityMode}
              onSelectMode={onSelectPersonalityMode}
              syncError={personalitySyncError}
              bridgeConnected={bridge.bridgeConnected}
            />
          }
        />
      </aside>
      <header className="app-shell__header">
        <StatusCards bridge={bridge} />
      </header>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}
