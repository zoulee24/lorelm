// 使用常量对象代替 enum
export const ContentTypeEnum = {
  JSON: 'application/json;charset=UTF-8',
  TEXT: 'text/plain;charset=UTF-8',
  FORM_URLENCODED: 'application/x-www-form-urlencoded;charset=UTF-8',
  FORM_DATA: 'multipart/form-data;charset=UTF-8',
};

// 同时定义类型以便于类型推导
export type ContentTypeEnum = typeof ContentTypeEnum[keyof typeof ContentTypeEnum];