import { formatMessageTime } from "../../utils/format";
import type { Conversation } from "../../types/transcript";

type ConversationListProps = {
  conversations: Conversation[];
  selectedConversationId: string | null;
  onSelect: (conversationId: string) => void;
};

function previewText(conversation: Conversation): string {
  const lastMessage = conversation.messages.at(-1);
  if (!lastMessage) {
    return "No messages yet";
  }
  return lastMessage.text;
}

export function ConversationList({
  conversations,
  selectedConversationId,
  onSelect,
}: ConversationListProps) {
  if (conversations.length === 0) {
    return (
      <div className="conversation-list conversation-list--empty">
        <p>No conversations yet.</p>
        <p className="conversation-list__hint">
          Transcript messages from the bridge will appear here.
        </p>
      </div>
    );
  }

  return (
    <ul className="conversation-list" aria-label="Conversations">
      {conversations.map((conversation) => {
        const isActive = conversation.id === selectedConversationId;
        return (
          <li key={conversation.id} className="conversation-list__item">
            <button
              type="button"
              className={
                isActive
                  ? "conversation-list__button conversation-list__button--active"
                  : "conversation-list__button"
              }
              aria-current={isActive ? "true" : undefined}
              onClick={() => onSelect(conversation.id)}
            >
              <span className="conversation-list__title">{conversation.title}</span>
              <span className="conversation-list__preview">{previewText(conversation)}</span>
              <time
                className="conversation-list__time"
                dateTime={new Date(conversation.updatedAt * 1000).toISOString()}
              >
                {formatMessageTime(conversation.updatedAt)}
              </time>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
