import type { SessionResponse, SessionMessageResponse, ConversationCreateForm } from "@/schemas/conversation";
import request from "@/utils/request";

const session = {
    list: () => request.get<SessionResponse[]>(`/conversation`),
    info: (session_id: number) => request.get<SessionMessageResponse>(`/conversation/${session_id}`),
    create: (data: ConversationCreateForm) => request.post<SessionMessageResponse>(`/conversation`, { body: data }),
    chat: (content: string, session: number) => request.stream<any>(`/conversation/${session}`, { body: { content }, method: "POST", parse: true }),
  }

export default {
  session
}
export {session as sessionApi}