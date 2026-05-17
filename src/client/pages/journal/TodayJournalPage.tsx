import { App, Alert, Flex, Space, Typography } from 'antd'
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { resolveApiErrorMessage } from '../../lib/error'
import {
  createJournalEntry,
  createReliefFeedback,
  fetchTodayQuestion,
} from '../../lib/journal'
import type { DailyQuestion, JournalEntry } from '../../lib/types'
import DailyQuestionPanel from './components/DailyQuestionPanel'
import JournalEditor from './components/JournalEditor'
import ReliefButton from './components/ReliefButton'
import ReflectionPreview from './components/ReflectionPreview'

export default function TodayJournalPage() {
  const { message } = App.useApp()
  const [question, setQuestion] = useState<DailyQuestion | null>(null)
  const [questionLoading, setQuestionLoading] = useState(false)
  const [questionError, setQuestionError] = useState<string | null>(null)
  const [content, setContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [reliefLoading, setReliefLoading] = useState(false)
  const [savedEntry, setSavedEntry] = useState<JournalEntry | null>(null)

  const loadQuestion = useCallback(async () => {
    setQuestionLoading(true)
    setQuestionError(null)
    try {
      const data = await fetchTodayQuestion()
      setQuestion(data)
    } catch (error) {
      const text = resolveApiErrorMessage(error, '暂时无法读取今日问题。')
      setQuestionError(text)
    } finally {
      setQuestionLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadQuestion()
  }, [loadQuestion])

  const handleSave = async () => {
    if (!question || !content.trim()) {
      return
    }

    setSaving(true)
    try {
      const entry = await createJournalEntry({
        question_id: question.id,
        content,
      })
      setSavedEntry(entry)
      setContent('')
      message.success('已保存')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '保存失败，请稍后再试。'))
    } finally {
      setSaving(false)
    }
  }

  const handleRelief = async () => {
    if (!savedEntry) {
      return
    }

    setReliefLoading(true)
    try {
      const feedback = await createReliefFeedback(savedEntry.id)
      setSavedEntry({
        ...savedEntry,
        relief_count: feedback.relief_count,
        has_relief_feedback: feedback.has_relief_feedback,
      })
      message.success('已记录')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '记录失败，请稍后再试。'))
    } finally {
      setReliefLoading(false)
    }
  }

  return (
    <Flex vertical gap={20}>
      <Space direction="vertical" size={4}>
        <Typography.Title level={2} style={{ margin: 0 }}>
          今日书写
        </Typography.Title>
        <Typography.Text type="secondary">
          没有进度条，没有评分，只是把此刻看清一点。
        </Typography.Text>
      </Space>

      <DailyQuestionPanel question={question} loading={questionLoading} error={questionError} />

      <JournalEditor
        value={content}
        saving={saving}
        disabled={!question || questionLoading}
        onChange={setContent}
        onSave={handleSave}
      />

      {savedEntry && (
        <Flex vertical gap={12}>
          <Alert type="success" showIcon message="这篇日记已经保存。" />
          <ReflectionPreview entry={savedEntry} />
          <Flex align="center" justify="space-between" wrap="wrap" gap={12}>
            <ReliefButton
              loading={reliefLoading}
              hasFeedback={savedEntry.has_relief_feedback}
              reliefCount={savedEntry.relief_count}
              onClick={handleRelief}
            />
            <Link to="/journal/recent">查看最近 7 天</Link>
          </Flex>
        </Flex>
      )}
    </Flex>
  )
}

