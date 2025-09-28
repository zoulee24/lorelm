import type { PageQuery, PageResponse } from "@/schemas/base";
import type {
  CharacterResponse,
  CharacterCreateForm,
  WorldCreateForm,
  DocumentResponse,
  DocumentCreateRequest,
  DocumentUpdateRequest,
  LabelResponse,
  WorldFullResponse,
} from "@/schemas/character";
import { objectToFormData, request } from "@/utils";

// Character APIs
const list = (query_params?: PageQuery) =>
  request.get<PageResponse<CharacterResponse>>("/character", { params: query_params })

const info = (character_id?: number) =>
  character_id ? request.get<CharacterResponse>(`/character/${character_id}`) : request.get<CharacterResponse>(`/character/info`)

const create = (data: FormData) =>
  request.post<CharacterResponse>("/character", { form: data })

const update = (character_id: number, data: CharacterCreateForm) =>
  request.put<CharacterResponse>(`/character/${character_id}`, { form: objectToFormData(data) })

const del = (character_id: number) =>
  request.delete<null>(`/character/${character_id}`)

// World APIs
const world = {
  list: (query_params?: PageQuery) =>
    request.get<PageResponse<WorldFullResponse>>("/world", { params: query_params }),

  info: (world_id?: number) =>
    world_id ? request.get<WorldFullResponse>(`/world/${world_id}`) : request.get<WorldFullResponse>(`/world/info`),

  characters: (world_id: number) =>
    request.get<CharacterResponse[]>(`/world/${world_id}/characters`),

  stream: (query: string) => 
    request.get<LabelResponse[]>('/world/stream', { params: { name: query} }),

  create: (data: FormData) =>
    request.post<WorldFullResponse>("/world", { form: data }),

  update: (world_id: number, data: WorldCreateForm) =>
    request.put<WorldFullResponse>(`/world/${world_id}`, { body: objectToFormData(data) }),

  del: (world_id: number) =>
    request.delete<WorldFullResponse>(`/world/${world_id}`)
}


const document = {
  listDocuments: (query_params?: PageQuery) =>
    request.get<PageResponse<DocumentResponse>>("/document", { params: query_params }),

  getDocument: (document_id?: number) =>
    document_id ? request.get<DocumentResponse>(`/document/${document_id}`) : request.get<DocumentResponse>(`/document/info`),

  createDocument: (data: DocumentCreateRequest) =>
    request.post<DocumentResponse>("/document", { body: objectToFormData(data) }),

  updateDocument: (document_id: number, data: DocumentUpdateRequest) =>
    request.put<DocumentResponse>(`/document/${document_id}`, { body: objectToFormData(data) }),

  deleteDocument: (document_id: number) =>
    request.delete<DocumentResponse>(`/document/${document_id}`)
}

const label = {
  stream: (query: string) => request.get<LabelResponse[]>('/label/stream', { params: { name: query} })
}

export default {
  list,
  info,
  create,
  update,
  del,
  label,
  world,
  document,
}
export {world, document}