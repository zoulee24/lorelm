import type { PageQuery, PageResponse } from "@/schemas/base";
import type { ConversationSession } from "@/schemas/conversation";
import request from "@/utils/request";

export default {
  session: {
    list: () => request.get<PageResponse<ConversationSession>>(`/conversation`)
  }
}