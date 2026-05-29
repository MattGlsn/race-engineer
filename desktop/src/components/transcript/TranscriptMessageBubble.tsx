import { formatMessageTime } from "../../utils/format";
import type { TranscriptMessage } from "../../types/transcript";

type TranscriptMessageBubbleProps = {
  message: TranscriptMessage;
};

const ROLE_LABELS = {
  driver: "Driver",
  engineer: "Engineer",
} as const;

export function TranscriptMessageBubble({ message }: TranscriptMessageBubbleProps) {
  return (
    <article
      className={`transcript-message transcript-message--${message.role}`}
      aria-label={`${ROLE_LABELS[message.role]} message`}
    >
      <header className="transcript-message__meta">
        <span className="transcript-message__role">{ROLE_LABELS[message.role]}</span>
        <time className="transcript-message__time" dateTime={new Date(message.ts * 1000).toISOString()}>
          {formatMessageTime(message.ts)}
        </time>
      </header>
      <p className="transcript-message__text">{message.text}</p>
    </article>
  );
}
