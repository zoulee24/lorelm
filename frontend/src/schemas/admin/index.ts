import type { ORMBase } from "../base"

export interface UserLoginForm {
  /** 邮箱 */
  username: string
  /** 密码 */
  password: string
}

export interface UserResponse extends ORMBase {
  /** 邮箱 */
  email: string
  /** 昵称 */
  nickname: string
  /** 密码 */
  password: string
  /** 头像 */
  avatar?: string
  /** 电话 */
  telephone?: string
  /** 性别 */
  gender?: string
  /** 禁用 */
  disabled: boolean
  /** 登录时间 */
  login_at?: Date
  /** 语言 */
  language: string
}

export interface UserCreateForm {
  /** 邮箱 */
  email: string
  /** 昵称 */
  nickname: string
  /** 密码 */
  password: string
  // /** 头像 */
  // avatar?: string
  /** 电话 */
  telephone?: string
  /** 性别 */
  gender?: string
  /** 语言 */
  language: string
}

export interface UserUpdateRequest extends UserCreateForm {
  /** 禁用 */
  disabled: boolean
}