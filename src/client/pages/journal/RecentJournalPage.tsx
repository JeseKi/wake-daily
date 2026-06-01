import { App, Alert, Button, Card, Empty, Flex, Select, Space, Spin, Tag, Typography } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import { listRecentAwarenessSessions } from '../../lib/journal'
import type { AwarenessSession } from '../../lib/types'

const dayOptions = [
  { value: 7, label: '最近 7 天' },
  { value: 30, label: '最近 30 天' },
  { value: 90, label: '最近 90 天' },
]

export default function RecentJournalPage() {
  const { message } = App.useApp()
  const [days, setDays] = useState(30)
  const [sessions, setSessions] = useState<AwarenessSession[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSessions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setSessions(await listRecentAwarenessSessions(days))
    } catch (err) {
      const text = resolveApiErrorMessage(err, '暂时无法读取觉察本。')
      setError(text)
      message.error(text)
    } finally {
      setLoading(false)
    }
  }, [days, message])

  useEffect(() => {
    void loadSessions()
  }, [loadSessions])

  return (
    <Flex vertical gap={20}>
      <Flex align="center" justify="space-between" gap={12} wrap="wrap">
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            我的觉察本
          </Typography.Title>
          <Typography.Text type="secondary">按水流一样的顺序，回看自己看见过的时刻。</Typography.Text>
        </Space>
        <Space wrap>
          <Select value={days} options={dayOptions} onChange={setDays} style={{ width: 132 }} />
          <Button icon={<ReloadOutlined />} onClick={loadSessions} loading={loading}>
            刷新
          </Button>
        </Space>
      </Flex>

      {error && <Alert type="error" showIcon message={error} />}

      {loading ? (
        <Flex justify="center" style={{ padding: 48 }}>
          <Spin />
        </Flex>
      ) : sessions.length === 0 ? (
        <Empty description="这段时间还没有觉察日记" />
      ) : (
        <Flex vertical gap={16}>
          {sessions.map((session) => (
            <Card key={session.id} className="forest-card">
              <Space direction="vertical" size={14} style={{ width: '100%' }}>
                <Flex align="center" justify="space-between" gap={12} wrap="wrap">
                  <Typography.Text strong>{session.submitted_on}</Typography.Text>
                  <Tag color="green">{session.emotion_label}</Tag>
                </Flex>
                <Section title="第一关 · 客观记录">
                  {session.objective_events.map((event, index) => (
                    <Typography.Paragraph key={index} style={{ marginBottom: 4 }}>
                      {index + 1}. {event}
                    </Typography.Paragraph>
                  ))}
                </Section>
                <Section title="第二关 · 情绪标记">
                  <Typography.Paragraph style={{ marginBottom: 4 }}>
                    触动事件：{session.objective_events[session.selected_event_index]}
                  </Typography.Paragraph>
                  <Typography.Paragraph style={{ marginBottom: 0 }}>
                    触发点：{session.emotion_note}
                  </Typography.Paragraph>
                </Section>
                <Section title="第三关 · 当下锚点">
                  <Typography.Paragraph style={{ marginBottom: 0 }}>
                    {session.present_anchor}
                  </Typography.Paragraph>
                </Section>
                {(session.review_comment || session.reward_label || session.review_score !== null) && (
                  <Alert
                    type="info"
                    showIcon
                    message="教师回应"
                    description={[
                      session.review_score !== null ? `评分：${session.review_score}/5` : '',
                      session.reward_label ? `奖励：${session.reward_label}` : '',
                      session.review_comment ?? '',
                    ]
                      .filter(Boolean)
                      .join(' · ')}
                  />
                )}
              </Space>
            </Card>
          ))}
        </Flex>
      )}
    </Flex>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <Typography.Text type="secondary">{title}</Typography.Text>
      <div style={{ marginTop: 6 }}>{children}</div>
    </div>
  )
}
