import type { TranscriptMessage } from "../../types/transcript";
import { TranscriptMessageBubble } from "./TranscriptMessageBubble";

type TranscriptMessageListProps = {
  messages: TranscriptMessage[];
  conversationTitle: string | null;
};

export function TranscriptMessageList({
  messages,
  conversationTitle,
}: TranscriptMessageListProps) {
  if (!conversationTitle) {
    return (
      <div className="transcript-message-list transcript-message-list--empty">
        <p>Select a conversation to view messages.</p>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="transcript-message-list transcript-message-list--empty">
        <p>No messages yet. Transcript updates will appear here in real time.</p>
      </div>
    );
  }

  return (
    <div className="transcript-message-list" role="log" aria-label={`${conversationTitle} transcript`}>
      {messages.map((message) => (
        <TranscriptMessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
}
