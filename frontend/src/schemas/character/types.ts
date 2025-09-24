import { DataRange } from "../base";

export const CharacterDataRange = {
  /** hèpnCP */
  all: DataRange.all,
  /** Åê«pn */
  self: DataRange.self,
  /** êšIpnCP */
  custom: DataRange.custom,
} as const;

export type CharacterDataRange = typeof CharacterDataRange[keyof typeof CharacterDataRange];