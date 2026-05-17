import api from './api'
import type {
  AdminScope,
  AdminScopeUpdatePayload,
  AdminUser,
  AdminUserCreatePayload,
  AdminUserScopesUpdatePayload,
  AdminUserUpdatePayload,
} from './types'

export async function createUser(payload: AdminUserCreatePayload): Promise<AdminUser> {
  const { data } = await api.post<AdminUser>('/admin/users', payload)
  return data
}

export async function listUsers(): Promise<AdminUser[]> {
  const { data } = await api.get<AdminUser[]>('/admin/users')
  return data
}

export async function updateUser(
  userId: number,
  payload: AdminUserUpdatePayload,
): Promise<AdminUser> {
  const { data } = await api.patch<AdminUser>(`/admin/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId: number): Promise<void> {
  await api.delete(`/admin/users/${userId}`)
}

export async function listScopes(): Promise<AdminScope[]> {
  const { data } = await api.get<AdminScope[]>('/admin/scopes')
  return data
}

export async function updateScope(
  scope: string,
  payload: AdminScopeUpdatePayload,
): Promise<AdminScope> {
  const { data } = await api.patch<AdminScope>(`/admin/scopes/${encodeURIComponent(scope)}`, payload)
  return data
}

export async function updateUserScopes(
  userId: number,
  payload: AdminUserScopesUpdatePayload,
): Promise<AdminUser> {
  const { data } = await api.put<AdminUser>(`/admin/users/${userId}/scopes`, payload)
  return data
}
