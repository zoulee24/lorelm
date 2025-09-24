import { DataRange } from "../base";

export const CharacterDataRange = {
  /** h�pnCP */
  all: DataRange.all,
  /** ��pn */
  self: DataRange.self,
  /** �IpnCP */
  custom: DataRange.custom,
} as const;

export type CharacterDataRange = typeof CharacterDataRange[keyof typeof CharacterDataRange];