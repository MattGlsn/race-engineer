const MODIFIER_KEYS = new Set([
  "Control",
  "Shift",
  "Alt",
  "Meta",
  "OS",
]);

const CODE_TO_TOKEN: Record<string, string> = {
  Space: "space",
  Enter: "enter",
  Tab: "tab",
  Backspace: "backspace",
  Delete: "delete",
  Escape: "escape",
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
};

for (let digit = 0; digit <= 9; digit += 1) {
  CODE_TO_TOKEN[`Digit${digit}`] = String(digit);
}

for (let index = 1; index <= 12; index += 1) {
  CODE_TO_TOKEN[`F${index}`] = `f${index}`;
}

for (const letter of "abcdefghijklmnopqrstuvwxyz") {
  CODE_TO_TOKEN[`Key${letter.toUpperCase()}`] = letter;
}

const TOKEN_LABELS: Record<string, string> = {
  ctrl: "Ctrl",
  shift: "Shift",
  alt: "Alt",
  cmd: "Cmd",
  win: "Win",
  space: "Space",
  enter: "Enter",
  tab: "Tab",
  backspace: "Backspace",
  delete: "Delete",
  escape: "Escape",
  up: "Up",
  down: "Down",
  left: "Left",
  right: "Right",
};

export function formatHotkeyLabel(spec: string): string {
  return spec
    .split("+")
    .filter(Boolean)
    .map((token) => {
      const lower = token.toLowerCase();
      if (TOKEN_LABELS[lower]) {
        return TOKEN_LABELS[lower];
      }
      if (lower.length === 1) {
        return lower.toUpperCase();
      }
      if (/^f\d+$/.test(lower)) {
        return lower.toUpperCase();
      }
      return token;
    })
    .join(" + ");
}

export function captureHotkeyFromKeyboardEvent(
  event: KeyboardEvent,
): string | null {
  if (event.key === "Escape") {
    return null;
  }

  if (MODIFIER_KEYS.has(event.key)) {
    return null;
  }

  const modifiers: string[] = [];
  if (event.ctrlKey) {
    modifiers.push("ctrl");
  }
  if (event.shiftKey) {
    modifiers.push("shift");
  }
  if (event.altKey) {
    modifiers.push("alt");
  }
  if (event.metaKey) {
    modifiers.push("win");
  }

  const keyToken = CODE_TO_TOKEN[event.code];
  if (!keyToken) {
    return null;
  }

  return [...modifiers, keyToken].join("+");
}

export function isValidHotkeySpec(spec: string): boolean {
  const parts = spec.split("+").filter(Boolean);
  if (parts.length === 0) {
    return false;
  }

  const modifierNames = new Set(["ctrl", "shift", "alt", "cmd", "win"]);
  const keys = parts.filter((part) => !modifierNames.has(part));
  return keys.length === 1;
}
