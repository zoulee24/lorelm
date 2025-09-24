export interface DbBase {}

export interface TableBase extends DbBase {
  /** 主键ID */
  id: number
}

export interface ORMBaseSmall extends TableBase {
  /** 创建时间 */
  created_at: Date
}

export interface ORMBase extends ORMBaseSmall {
  /** 更新时间 */
  updated_at: Date
}

export interface JwtToken {
  /** 访问令牌 */
  access_token: string
  /** 刷新令牌 */
  refresh_token: string
  /** 令牌类型 */
  token_type: string
}

export interface PageResponse<T> {
  /** 数据 */
  data: T[]
  /** 总条数 */
  total: number
}
export interface PageQuery {
  page: number
  limit: number
  search?: string
}
export { DataRange } from "./types"