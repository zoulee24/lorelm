import type { SessionResponse, SessionMessageResponse, ConversationCreateForm } from "@/schemas/conversation";
import request from "@/utils/request";

const session = {
    list: () => request.get<SessionResponse[]>(`/conversation`),
    info: (session_id: number) => request.get<SessionMessageResponse>(`/conversation/${session_id}`),
    create: (data: ConversationCreateForm | string, session_id?: number) => 
      request.stream<any>(`/conversation`, { body: data, method: "POST", params: { session_id}, parse: true })
  }

export default {
  session
}
export {session as sessionApi}