export type TranscriptRole = "driver" | "engineer";

export type TranscriptMessage = {
  id: string;
  role: TranscriptRole;
  text: string;
  ts: number;
};

export type Conversation = {
  id: string;
  title: string;
  trackName: string | null;
  sessionType: string | null;
  createdAt: number;
  updatedAt: number;
  messages: TranscriptMessage[];
};

export type TranscriptMessageData = {
  role: TranscriptRole;
  text: string;
  conversation_id?: string;
  track_name?: string | null;
  session_type?: string | null;
};

export type TranscriptStoreState = {
  conversations: Conversation[];
  selectedConversationId: string | null;
};
