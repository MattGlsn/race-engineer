import { useCallback, useEffect, useState } from "react";

import type {
  Conversation,
  TranscriptMessage,
  TranscriptMessageData,
  TranscriptStoreState,
} from "../types/transcript";
import {
  buildConversationId,
  buildConversationTitle,
  sortConversations,
} from "../utils/conversation";
import { loadTranscriptState, saveTranscriptState } from "../utils/transcriptStorage";

function createMessageId(ts: number): string {
  return `${ts}-${Math.random().toString(36).slice(2, 9)}`;
}

function initialState(): TranscriptStoreState {
  return loadTranscriptState() ?? {
    conversations: [],
    selectedConversationId: null,
  };
}

function upsertMessage(
  conversations: Conversation[],
  data: TranscriptMessageData,
  ts: number,
): { conversations: Conversation[]; selectedConversationId: string } {
  const conversationId = buildConversationId(data);
  const message: TranscriptMessage = {
    id: createMessageId(ts),
    role: data.role,
    text: data.text,
    ts,
  };

  const existingIndex = conversations.findIndex(
    (conversation) => conversation.id === conversationId,
  );

  if (existingIndex === -1) {
    const created: Conversation = {
      id: conversationId,
      title: buildConversationTitle(data),
      trackName: data.track_name ?? null,
      sessionType: data.session_type ?? null,
      createdAt: ts,
      updatedAt: ts,
      messages: [message],
    };
    return {
      conversations: sortConversations([created, ...conversations]),
      selectedConversationId: conversationId,
    };
  }

  const existing = conversations[existingIndex];
  const updated: Conversation = {
    ...existing,
    updatedAt: ts,
    messages: [...existing.messages, message],
  };
  const next = [...conversations];
  next[existingIndex] = updated;

  return {
    conversations: sortConversations(next),
    selectedConversationId: conversationId,
  };
}

export function useTranscriptStore() {
  const [state, setState] = useState<TranscriptStoreState>(initialState);

  useEffect(() => {
    saveTranscriptState(state);
  }, [state]);

  const handleIncoming = useCallback((data: TranscriptMessageData, ts: number) => {
    if (!data.text.trim()) {
      return;
    }
    setState((prev) => {
      const next = upsertMessage(prev.conversations, data, ts);
      return {
        conversations: next.conversations,
        // Always show the conversation that just received a message.
        selectedConversationId: next.selectedConversationId,
      };
    });
  }, []);

  const selectConversation = useCallback((conversationId: string) => {
    setState((prev) => ({
      ...prev,
      selectedConversationId: conversationId,
    }));
  }, []);

  const selectedConversation =
    state.conversations.find(
      (conversation) => conversation.id === state.selectedConversationId,
    ) ?? null;

  return {
    conversations: state.conversations,
    selectedConversation,
    selectedConversationId: state.selectedConversationId,
    handleIncoming,
    selectConversation,
  };
}
