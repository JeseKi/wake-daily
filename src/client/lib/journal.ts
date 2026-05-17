import api from './api'
import type {
  DailyQuestion,
  DailyQuestionPayload,
  DailyQuestionUpdatePayload,
  JournalEntry,
  JournalEntryPayload,
  ReliefFeedback,
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

