import { useCallback, useEffect, useRef } from "react";

const SCROLL_STORAGE_PREFIX = "race-engineer:transcript-scroll:";
const NEAR_BOTTOM_PX = 48;

function scrollStorageKey(conversationId: string): string {
  return `${SCROLL_STORAGE_PREFIX}${conversationId}`;
}

function readScrollTop(conversationId: string): number | null {
  try {
    const raw = sessionStorage.getItem(scrollStorageKey(conversationId));
    if (raw == null) {
      return null;
    }
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  } catch {
    return null;
  }
}

function writeScrollTop(conversationId: string, scrollTop: number): void {
  try {
    sessionStorage.setItem(scrollStorageKey(conversationId), String(scrollTop));
  } catch {
    // Ignore storage errors.
  }
}

function isNearBottom(element: HTMLElement): boolean {
  return element.scrollHeight - element.scrollTop - element.clientHeight <= NEAR_BOTTOM_PX;
}

export function useScrollPersistence(conversationId: string | null) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const stickToBottomRef = useRef(true);
  const saveTimerRef = useRef<number | null>(null);

  const clearSaveTimer = useCallback(() => {
    if (saveTimerRef.current != null) {
      window.clearTimeout(saveTimerRef.current);
      saveTimerRef.current = null;
    }
  }, []);

  const saveScrollPosition = useCallback(() => {
    const element = containerRef.current;
    if (!element || !conversationId) {
      return;
    }
    stickToBottomRef.current = isNearBottom(element);
    writeScrollTop(conversationId, element.scrollTop);
  }, [conversationId]);

  const scheduleSave = useCallback(() => {
    clearSaveTimer();
    saveTimerRef.current = window.setTimeout(saveScrollPosition, 100);
  }, [clearSaveTimer, saveScrollPosition]);

  useEffect(() => {
    const element = containerRef.current;
    if (!element || !conversationId) {
      return;
    }

    const savedScrollTop = readScrollTop(conversationId);
    if (savedScrollTop != null) {
      element.scrollTop = savedScrollTop;
      stickToBottomRef.current = isNearBottom(element);
    } else {
      element.scrollTop = element.scrollHeight;
      stickToBottomRef.current = true;
    }
  }, [conversationId]);

  useEffect(() => {
    const element = containerRef.current;
    if (!element || !conversationId) {
      return;
    }

    const onScroll = () => {
      scheduleSave();
    };

    element.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      element.removeEventListener("scroll", onScroll);
      clearSaveTimer();
      saveScrollPosition();
    };
  }, [clearSaveTimer, conversationId, saveScrollPosition, scheduleSave]);

  const scrollToLatestIfPinned = useCallback(() => {
    const element = containerRef.current;
    if (!element || !stickToBottomRef.current) {
      return;
    }
    element.scrollTop = element.scrollHeight;
    if (conversationId) {
      writeScrollTop(conversationId, element.scrollTop);
    }
  }, [conversationId]);

  return {
    containerRef,
    scrollToLatestIfPinned,
  };
}
