import type { PageQuery, PageResponse } from "@/schemas/base";
import type {
  CharacterResponse,
  CharacterCreateForm,
  WorldResponse,
  WorldCreateForm,
  DocumentResponse,
  DocumentCreateRequest,
  DocumentUpdateRequest,
} from "@/schemas/character";
import { objectToFormData, request } from "@/utils";

// Character APIs
const list = (query_params?: PageQuery) =>
  request.get<PageResponse<CharacterResponse>>("/character", { params: query_params })

const info = (character_id?: number) =>
  character_id ? request.get<CharacterResponse>(`/character/${character_id}`) : request.get<CharacterResponse>(`/character/info`)

const create = (data: CharacterCreateForm) =>
  request.post<CharacterResponse>("/character", { body: objectToFormData(data) })

const update = (character_id: number, data: CharacterCreateForm) =>
  request.put<CharacterResponse>(`/character/${character_id}`, { body: objectToFormData(data) })

const del = (character_id: number) =>
  request.delete<CharacterResponse>(`/character/${character_id}`)

// World APIs
const world = {
  list: (query_params?: PageQuery) =>
    request.get<PageResponse<WorldResponse>>("/world", { params: query_params }),

  info: (world_id?: number) =>
    world_id ? request.get<WorldResponse>(`/world/${world_id}`) : request.get<WorldResponse>(`/world/info`),

  create: (data: WorldCreateForm) =>
    request.post<WorldResponse>("/world", { body: objectToFormData(data) }),

  update: (world_id: number, data: WorldCreateForm) =>
    request.put<WorldResponse>(`/world/${world_id}`, { body: objectToFormData(data) }),

  del: (world_id: number) =>
    request.delete<WorldResponse>(`/world/${world_id}`)
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

export default {
  list,
  info,
  create,
  update,
  del,
  world,
  document,
}
export {world, document}