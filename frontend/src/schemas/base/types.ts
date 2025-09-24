export const DataRange = {
  /** 全部数据权限 */
  all: "all",
  /** 仅自身数据 */
  self: "self",
  /** 自定义数据权限 */
  custom: "custom",
} as const

export type DataRange = typeof DataRange[keyof typeof DataRange]