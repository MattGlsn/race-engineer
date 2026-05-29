export const PERSONALITY_MODES = ["calm", "direct", "intense"] as const;

export type PersonalityMode = (typeof PERSONALITY_MODES)[number];

export const DEFAULT_PERSONALITY_MODE: PersonalityMode = "direct";

export const PERSONALITY_MODE_LABELS: Record<PersonalityMode, string> = {
  calm: "Calm",
  direct: "Direct",
  intense: "Intense",
};

export const PERSONALITY_MODE_HINTS: Record<PersonalityMode, string> = {
  calm: "Calm and steady radio engineer; plain language, level emotions.",
  direct: "Direct and factual; lead with the answer, pit-wall brevity.",
  intense: "Urgent and energetic; decisive phrasing without exaggeration.",
};

export function isPersonalityMode(value: string): value is PersonalityMode {
  return (PERSONALITY_MODES as readonly string[]).includes(value);
}
