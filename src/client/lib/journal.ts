import api from './api'
import type {
  DailyQuestion,
  DailyQuestionPayload,
  DailyQuestionUpdatePayload,
  AdminAwarenessSession,
  AwarenessSession,
  AwarenessSessionPayload,
  AwarenessSessionReviewPayload,
  Growth,
  JournalAdminDashboard,
  JournalBinding,
  JournalClass,
  JournalClassPayload,
  JournalClassUpdatePayload,
  JournalEntry,
  JournalEntryPayload,
  ReliefFeedback,
  ResonanceFeedback,
  ResonanceItem,
  ResonanceItemPayload,
} from './types'

export async function fetchTodayQuestion(): Promise<DailyQuestion> {
  const { data } = await api.get<DailyQuestion>('/journal/today-question')
  return data
}

export async function createJournalEntry(payload: JournalEntryPayload): Promise<JournalEntry> {
  const { data } = await api.post<JournalEntry>('/journal/entries', payload)
  return data
}

export async function listRecentJournalEntries(days = 7): Promise<JournalEntry[]> {
  const { data } = await api.get<JournalEntry[]>('/journal/entries/recent', {
    params: { days },
  })
  return data
}

export async function createReliefFeedback(entryId: number): Promise<ReliefFeedback> {
  const { data } = await api.post<ReliefFeedback>(`/journal/entries/${entryId}/relief`)
  return data
}

export async function listDailyQuestions(): Promise<DailyQuestion[]> {
  const { data } = await api.get<DailyQuestion[]>('/admin/journal/questions')
  return data
}

export async function createDailyQuestion(payload: DailyQuestionPayload): Promise<DailyQuestion> {
  const { data } = await api.post<DailyQuestion>('/admin/journal/questions', payload)
  return data
}

export async function updateDailyQuestion(
  questionId: number,
  payload: DailyQuestionUpdatePayload,
): Promise<DailyQuestion> {
  const { data } = await api.patch<DailyQuestion>(`/admin/journal/questions/${questionId}`, payload)
  return data
}

export async function deleteDailyQuestion(questionId: number): Promise<void> {
  await api.delete(`/admin/journal/questions/${questionId}`)
}

export async function fetchMyJournalBinding(): Promise<JournalBinding> {
  const { data } = await api.get<JournalBinding>('/journal/me/binding')
  return data
}

export async function bindJournalClass(bindingCode: string): Promise<JournalBinding> {
  const { data } = await api.post<JournalBinding>('/journal/classes/bind', {
    binding_code: bindingCode,
  })
  return data
}

export async function createAwarenessSession(
  payload: AwarenessSessionPayload,
): Promise<AwarenessSession> {
  const { data } = await api.post<AwarenessSession>('/journal/sessions', payload)
  return data
}

export async function listRecentAwarenessSessions(days = 30): Promise<AwarenessSession[]> {
  const { data } = await api.get<AwarenessSession[]>('/journal/sessions/recent', {
    params: { days },
  })
  return data
}

export async function fetchGrowth(): Promise<Growth> {
  const { data } = await api.get<Growth>('/journal/growth')
  return data
}

export async function listResonanceItems(): Promise<ResonanceItem[]> {
  const { data } = await api.get<ResonanceItem[]>('/journal/resonance')
  return data
}

export async function createResonanceFeedback(itemId: number): Promise<ResonanceFeedback> {
  const { data } = await api.post<ResonanceFeedback>(`/journal/resonance/${itemId}/empathy`)
  return data
}

export async function listJournalClasses(): Promise<JournalClass[]> {
  const { data } = await api.get<JournalClass[]>('/admin/journal/classes')
  return data
}

export async function createJournalClass(payload: JournalClassPayload): Promise<JournalClass> {
  const { data } = await api.post<JournalClass>('/admin/journal/classes', payload)
  return data
}

export async function updateJournalClass(
  classId: number,
  payload: JournalClassUpdatePayload,
): Promise<JournalClass> {
  const { data } = await api.patch<JournalClass>(`/admin/journal/classes/${classId}`, payload)
  return data
}

export async function regenerateJournalClassCode(classId: number): Promise<JournalClass> {
  const { data } = await api.post<JournalClass>(
    `/admin/journal/classes/${classId}/regenerate-code`,
  )
  return data
}

export async function listAdminAwarenessSessions(
  classId?: number,
): Promise<AdminAwarenessSession[]> {
  const { data } = await api.get<AdminAwarenessSession[]>('/admin/journal/sessions', {
    params: classId ? { class_id: classId } : undefined,
  })
  return data
}

export async function reviewAwarenessSession(
  sessionId: number,
  payload: AwarenessSessionReviewPayload,
): Promise<AwarenessSession> {
  const { data } = await api.patch<AwarenessSession>(
    `/admin/journal/sessions/${sessionId}/review`,
    payload,
  )
  return data
}

export async function createResonanceItem(
  sessionId: number,
  payload: ResonanceItemPayload,
): Promise<ResonanceItem> {
  const { data } = await api.post<ResonanceItem>(
    `/admin/journal/sessions/${sessionId}/resonance`,
    payload,
  )
  return data
}

export async function deleteResonanceItem(itemId: number): Promise<void> {
  await api.delete(`/admin/journal/resonance/${itemId}`)
}

export async function fetchJournalAdminDashboard(): Promise<JournalAdminDashboard> {
  const { data } = await api.get<JournalAdminDashboard>('/admin/journal/dashboard')
  return data
}
