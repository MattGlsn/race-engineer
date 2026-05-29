import type { ReactNode } from "react";

import type { PersonalityMode } from "../../types/personalityMode";
import type { BridgeSocketState } from "../../hooks/useBridgeWebSocket";
import { EngineerToneControl } from "../settings/EngineerToneControl";
import { VoiceHotkeyControl } from "../settings/VoiceHotkeyControl";
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
  voiceHotkey: string;
  onSelectVoiceHotkey: (hotkey: string) => void;
  voiceHotkeySyncError: string | null;
  children: ReactNode;
};

export function AppShell({
  bridge,
  activeView,
  onNavigate,
  personalityMode,
  onSelectPersonalityMode,
  personalitySyncError,
  voiceHotkey,
  onSelectVoiceHotkey,
  voiceHotkeySyncError,
  children,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <SidebarNav
          activeId={activeView}
          onNavigate={onNavigate}
          footer={
            <div className="sidebar-settings">
              <VoiceHotkeyControl
                hotkey={voiceHotkey}
                onSelectHotkey={onSelectVoiceHotkey}
                syncError={voiceHotkeySyncError}
                bridgeConnected={bridge.bridgeConnected}
              />
              <EngineerToneControl
                mode={personalityMode}
                onSelectMode={onSelectPersonalityMode}
                syncError={personalitySyncError}
                bridgeConnected={bridge.bridgeConnected}
              />
            </div>
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
