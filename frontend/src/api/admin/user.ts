import type { UserLoginForm, UserResponse } from "@/schemas/admin";
import type { PageResponse, PageQuery, JwtToken } from "@/schemas/base";
import { objectToFormData, request } from "@/utils";

const list = (query_params?: PageQuery) =>
  request.get<PageResponse<UserResponse>>("/admin/user", {params: query_params})
const info = (user_id?: number) =>
  user_id ? request.get<UserResponse>(`/admin/user/${user_id}`) : request.get<UserResponse>(`/admin/user/info`)
const create = (data: FormData) =>
  request.post<UserResponse>("/admin/user", {form: data})

const update = (user_id: number, data: FormData) =>
  request.put<UserResponse>(`/admin/user/${user_id}`, {form: data})

const del = (user_id: number) =>
  request.delete<UserResponse>(`/admin/user/${user_id}`)

const login = (data: UserLoginForm) => 
  request.post<JwtToken>("/admin/user/login", {form: objectToFormData(data)})

const refresh = () =>
  request.post<JwtToken>("/admin/user/refresh")


export default {
  list,
  info,
  create,
  update,
  del,
  login,
  refresh
}
