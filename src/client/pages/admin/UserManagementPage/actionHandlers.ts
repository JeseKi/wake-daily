import type { AdminUser, AdminUserCreatePayload } from '../../../lib/types'
import type { FormInstance } from 'antd'
import type { MessageInstance } from 'antd/es/message/interface'
import { resolveErrorMessage } from './utils'
import { buildUpdatePayload, isPasswordMismatch } from './formHelpers'

export async function handleSave(params: {
  editingUser: AdminUser | null
  editForm: FormInstance
  message: MessageInstance
  setSaving: (saving: boolean) => void
  setUsers: (updater: (prev: AdminUser[]) => AdminUser[]) => void
  closeEditModal: () => void
}) {
  const { editingUser, editForm, message, setSaving, setUsers, closeEditModal } = params
  if (!editingUser) return

  try {
    const values = await editForm.validateFields()
    const payload = buildUpdatePayload(values, editingUser)

    if (Object.keys(payload).length === 0) {
      message.info('没有需要保存的改动')
      closeEditModal()
      return
    }

    setSaving(true)
    try {
      const { updateUser } = await import('../../../lib/admin')
      const updated = await updateUser(editingUser.id, payload)
      setUsers((prev) => prev.map((item) => (item.id === editingUser.id ? updated : item)))
      message.success('用户信息已更新')
      closeEditModal()
    } finally {
      setSaving(false)
    }
  } catch (err: unknown) {
    if (typeof err === 'object' && err && 'errorFields' in err) return
    message.error(resolveErrorMessage(err))
  }
}

export async function handleResetPassword(params: {
  resettingUser: AdminUser | null
  resetPasswordForm: FormInstance
  message: MessageInstance
  setResettingPassword: (resetting: boolean) => void
  setUsers: (updater: (prev: AdminUser[]) => AdminUser[]) => void
  closeResetPasswordModal: () => void
}) {
  const { resettingUser, resetPasswordForm, message, setResettingPassword, setUsers, closeResetPasswordModal } = params
  if (!resettingUser) return

  try {
    const values = await resetPasswordForm.validateFields()
    setResettingPassword(true)
    try {
      const { updateUser } = await import('../../../lib/admin')
      const updated = await updateUser(resettingUser.id, { password: values.password })
      setUsers((prev) => prev.map((item) => (item.id === resettingUser.id ? updated : item)))
      message.success(`已重置用户 ${resettingUser.username} 的密码`)
      closeResetPasswordModal()
    } finally {
      setResettingPassword(false)
    }
  } catch (err: unknown) {
    if (typeof err === 'object' && err && 'errorFields' in err) return
    message.error(resolveErrorMessage(err))
  }
}

export async function handleDeleteUser(params: {
  deletingUser: AdminUser | null
  deleteForm: FormInstance
  editingUser: AdminUser | null
  message: MessageInstance
  setDeleting: (deleting: boolean) => void
  setUsers: (updater: (prev: AdminUser[]) => AdminUser[]) => void
  closeDeleteModal: () => void
  closeEditModal: () => void
}) {
  const { deletingUser, deleteForm, editingUser, message, setDeleting, setUsers, closeDeleteModal, closeEditModal } = params
  if (!deletingUser) return

  try {
    await deleteForm.validateFields()
    setDeleting(true)
    try {
      const { deleteUser } = await import('../../../lib/admin')
      await deleteUser(deletingUser.id)
      setUsers((prev) => prev.filter((item) => item.id !== deletingUser.id))
      if (editingUser?.id === deletingUser.id) closeEditModal()
      message.success(`已删除用户 ${deletingUser.username}`)
      closeDeleteModal()
    } finally {
      setDeleting(false)
    }
  } catch (err: unknown) {
    if (typeof err === 'object' && err && 'errorFields' in err) return
    message.error(resolveErrorMessage(err))
  }
}

export async function handleCreate(params: {
  createForm: FormInstance
  message: MessageInstance
  setCreating: (creating: boolean) => void
  setUsers: (updater: (prev: AdminUser[]) => AdminUser[]) => void
  closeCreateModal: () => void
}) {
  const { createForm, message, setCreating, setUsers, closeCreateModal } = params

  try {
    const values = await createForm.validateFields()
    if (isPasswordMismatch(values)) {
      message.error('两次输入的密码不一致')
      return
    }
    const payload: AdminUserCreatePayload = {
      username: values.username.trim(),
      email: values.email.trim().toLowerCase(),
      name: values.name?.trim() || null,
      role: values.role,
      status: values.status,
      password: values.password,
    }

    setCreating(true)
    try {
      const { createUser } = await import('../../../lib/admin')
      const created = await createUser(payload)
      setUsers((prev) => [created, ...prev])
      message.success(`已创建用户 ${created.username}`)
      closeCreateModal()
    } finally {
      setCreating(false)
    }
  } catch (err: unknown) {
    if (typeof err === 'object' && err && 'errorFields' in err) return
    message.error(resolveErrorMessage(err))
  }
}

