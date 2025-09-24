import type { DataRange, ORMBase } from "../base";

/**
 * 角色标签接口
 */
export interface LabelResponse extends ORMBase {
  /** 标签名称 */
  name: string;
}

/**
 * 世界响应接口
 */
export interface WorldResponse extends ORMBase {
  /** 昵称 */
  nickname: string;
  /** 描述 */
  description: string;
  /** 数据范围 */
  data_range: DataRange;
  /** 标签 */
  labels: string[];
  /** 拥有用户ID */
  user_id: number;
}

/**
 * 角色响应接口
 */
export interface CharacterResponse extends ORMBase {
  /** 昵称 */
  nickname: string;
  /** 描述 */
  description: string;
  /** 首条信息 */
  first_message: string;
  /** 数据范围 */
  data_range: DataRange;
  /** 标签 */
  labels: string[];
  /** 拥有用户ID */
  user_id: number;
}

/**
 * 文档响应接口
 */
export interface DocumentResponse extends ORMBase {
  /** 角色ID */
  character_id: number | null;
  /** 世界ID */
  world_id: number | null;
  /** 内容 */
  content: string;
  /** 是否禁用 */
  disabled: boolean;
  /** 数据范围 */
  data_range: DataRange;
}

/**
 * 世界创建表单
 */
export interface WorldCreateForm {
  /** 昵称 */
  nickname: string;
  /** 描述 */
  description?: string;
  /** 数据范围 */
  data_range: DataRange;
  /** 标签列表 */
  labels?: string[];
}

/**
 * 角色创建表单
 */
export interface CharacterCreateForm {
  /** 昵称 */
  nickname: string;
  /** 描述 */
  description: string;
  /** 首条信息 */
  first_message: string;
  /** 数据范围 */
  data_range: DataRange;
  /** 标签列表 */
  labels?: string[];
}

/**
 * 文档创建请求
 */
export interface DocumentCreateRequest {
  /** 角色ID */
  character_id?: number;
  /** 内容 */
  content: string;
  /** 是否禁用 */
  disabled?: boolean;
  /** 数据范围 */
  data_range: DataRange;
}

/**
 * 文档更新请求
 */
export interface DocumentUpdateRequest extends DocumentCreateRequest {
  /** 文档ID */
  id: number;
}