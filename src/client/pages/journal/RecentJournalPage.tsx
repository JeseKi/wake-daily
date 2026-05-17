import { App, Alert, Button, Empty, Flex, Select, Space, Spin, Typography } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import { createReliefFeedback, listRecentJournalEntries } from '../../lib/journal'
import type { JournalEntry } from '../../lib/types'
import ReflectionPreview from './components/ReflectionPreview'
import ReliefButton from './components/ReliefButton'

const dayOptions = [
  { value: 7, label: '最近 7 天' },
  { value: 14, label: '最近 14 天' },
  { value: 30, label: '最近 30 天' },
]

export default function RecentJournalPage() {
  const { message } = App.useApp()
  const [days, setDays] = useState(7)
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reliefLoadingId, setReliefLoadingId] = useState<number | null>(null)

  const loadEntries = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listRecentJournalEntries(days)
      setEntries(data)
    } catch (err) {
      const text = resolveApiErrorMessage(err, '暂时无法读取最近日记。')
      setError(text)
      message.error(text)
    } finally {
      setLoading(false)
    }
  }, [days, message])

  useEffect(() => {
    void loadEntries()
  }, [loadEntries])

  const handleRelief = async (entry: JournalEntry) => {
    setReliefLoadingId(entry.id)
    try {
      const feedback = await createReliefFeedback(entry.id)
      setEntries((prev) =>
        prev.map((item) =>
          item.id === entry.id
            ? {
                ...item,
                relief_count: feedback.relief_count,
                has_relief_feedback: feedback.has_relief_feedback,
              }
            : item,
        ),
      )
      message.success('已记录')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '记录失败，请稍后再试。'))
    } finally {
      setReliefLoadingId(null)
    }
  }

  return (
    <Flex vertical gap={20}>
      <Flex align="center" justify="space-between" gap={12} wrap="wrap">
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            最近回看
          </Typography.Title>
          <Typography.Text type="secondary">
            被高亮的词只是提醒，不是评判。
          </Typography.Text>
        </Space>
        <Space wrap>
          <Select value={days} options={dayOptions} onChange={setDays} style={{ width: 132 }} />
          <Button icon={<ReloadOutlined />} onClick={loadEntries} loading={loading}>
            刷新
          </Button>
        </Space>
      </Flex>

      {error && <Alert type="error" showIcon message={error} />}

      {loading ? (
        <Flex justify="center" style={{ padding: 48 }}>
          <Spin />
        </Flex>
      ) : entries.length === 0 ? (
        <Empty description="这段时间还没有日记" />
      ) : (
        <Flex vertical gap={16}>
          {entries.map((entry) => (
            <Flex vertical gap={8} key={entry.id}>
              <ReflectionPreview entry={entry} />
              <ReliefButton
                loading={reliefLoadingId === entry.id}
                hasFeedback={entry.has_relief_feedback}
                reliefCount={entry.relief_count}
                onClick={() => handleRelief(entry)}
              />
            </Flex>
          ))}
        </Flex>
      )}
    </Flex>
  )
}

