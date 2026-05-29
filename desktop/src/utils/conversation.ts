import type { Conversation, TranscriptMessageData } from "../types/transcript";

export function buildConversationId(data: TranscriptMessageData): string {
  if (data.conversation_id) {
    return data.conversation_id;
  }
  const track = data.track_name?.trim() || "unknown-track";
  const session = data.session_type?.trim() || "unknown-session";
  return `${track}::${session}`.toLowerCase().replace(/\s+/g, "-");
}

export function buildConversationTitle(data: TranscriptMessageData): string {
  const track = data.track_name?.trim();
  const session = data.session_type?.trim();
  if (track && session) {
    return `${track} — ${session}`;
  }
  if (track) {
    return track;
  }
  if (session) {
    return session;
  }
  return "Session";
}

export function sortConversations(conversations: Conversation[]): Conversation[] {
  return [...conversations].sort((a, b) => b.updatedAt - a.updatedAt);
}
