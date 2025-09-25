import type { ORMBase, ORMBaseSmall } from "../base";
import type { CharacterResponse, WorldResponse } from "../character";

/**
 * 对话会话接口
 */
export interface SessionResponse extends ORMBase {
  /** 用户ID */
  user_id: number;
  /** 世界ID */
  world_id?: number;
  /** 用户扮演的角色ID */
  act_character_id?: number;
  /** 会话标题 */
  title: string;
  /** 对话消耗的token数 */
  token_usage: number;
}

export interface SessionFullResponse extends SessionResponse {
  world?: WorldResponse;
  act_character?: CharacterResponse;
  /** 角色 */
  characters?: CharacterResponse[];
}

export interface SessionMessageResponse extends SessionFullResponse {
  /** 消息 */
  messages: ConversationHistory[];
}

/**
 * 对话角色枚举
 */
export type ConversationRole = "user" | "assistant";

/**
 * 对话历史接口
 */
export interface ConversationHistory extends ORMBase {
  /** 会话ID */
  session_id: number;
  /** 消息ID */
  message_id: string;
  /** 角色 */
  role: ConversationRole;
  /** 对话内容 */
  content: string;
  /** 推理过程 */
  reasoning?: string;
  /** 对话消耗的token数 */
  token_usage: number;
  /** 会话 */
  session?: SessionResponse;
}

/**
 * 对话创建表单
 */
export interface ConversationCreateForm {
  /** 世界ID */
  world_id?: number;
  /** 用户扮演的角色ID */
  act_character_id?: number;
  character_ids: number[];
  /** 会话内容 */
  content: string;
}

// /**
//  * 消息发送表单
//  */
// export interface MessageSendForm {
//   /** 会话ID */
//   session_id: number;
//   /** 对话内容 */
//   content?: string;
// }

/**
 * 对话历史响应
 */
export interface ConversationHistoryResponse extends ORMBaseSmall {
  /** 消息ID */
  message_id: string;
  /** 角色 */
  role: ConversationRole;
  /** 对话内容 */
  content: string;
  /** 推理过程 */
  reasoning?: string;
  /** 对话消耗的token数 */
  token_usage: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  reasoning?: string;
  refs?: any[]
  finished?: boolean;
}