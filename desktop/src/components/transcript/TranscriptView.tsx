import type { Conversation } from "../../types/transcript";
import { ConversationList } from "./ConversationList";
import { TranscriptMessageList } from "./TranscriptMessageList";

type TranscriptViewProps = {
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  selectedConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
};

export function TranscriptView({
  conversations,
  selectedConversation,
  selectedConversationId,
  onSelectConversation,
}: TranscriptViewProps) {
  return (
    <section className="transcript-view" aria-label="Transcript">
      <aside className="transcript-view__sidebar">
        <header className="transcript-view__sidebar-header">
          <h2 className="transcript-view__heading">Conversations</h2>
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
        <TranscriptMessageList
          conversationId={selectedConversationId}
          conversationTitle={selectedConversation?.title ?? null}
          messages={selectedConversation?.messages ?? []}
        />
      </div>
    </section>
  );
}
