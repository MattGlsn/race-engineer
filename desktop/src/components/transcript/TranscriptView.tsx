import type { Conversation } from "../../types/transcript";
import { ConversationList } from "./ConversationList";
import { EngineerVolumeControl } from "./EngineerVolumeControl";
import { TranscriptMessageList } from "./TranscriptMessageList";
import { VoiceRecordingIndicator } from "./VoiceRecordingIndicator";

type TranscriptViewProps = {
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  selectedConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  voiceVolume: number;
  onChangeVoiceVolume: (volume: number) => void;
  voiceVolumeSyncError: string | null;
  bridgeConnected: boolean;
  voiceStatus: "recording" | "idle";
};

export function TranscriptView({
  conversations,
  selectedConversation,
  selectedConversationId,
  onSelectConversation,
  voiceVolume,
  onChangeVoiceVolume,
  voiceVolumeSyncError,
  bridgeConnected,
  voiceStatus,
}: TranscriptViewProps) {
  return (
    <section className="transcript-view" aria-label="Transcript">
      <aside className="transcript-view__sidebar">
        <header className="transcript-view__sidebar-header">
          <h2 className="transcript-view__heading">Conversations</h2>
          <EngineerVolumeControl
            volume={voiceVolume}
            onChangeVolume={onChangeVoiceVolume}
            syncError={voiceVolumeSyncError}
            bridgeConnected={bridgeConnected}
          />
        </header>
        <ConversationList
          conversations={conversations}
          selectedConversationId={selectedConversationId}
          onSelect={onSelectConversation}
        />
      </aside>
      <div className="transcript-view__panel">
        <header className="transcript-view__panel-header">
          <h2 className="transcript-view__heading">
            {selectedConversation?.title ?? "Transcript"}
          </h2>
        </header>
        <VoiceRecordingIndicator status={voiceStatus} />
        <TranscriptMessageList
          conversationId={selectedConversationId}
          conversationTitle={selectedConversation?.title ?? null}
          messages={selectedConversation?.messages ?? []}
        />
      </div>
    </section>
  );
}
