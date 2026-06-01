import { App, Button, Card, Empty, Flex, Space, Spin, Typography } from 'antd'
import { BulbOutlined, ReloadOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import { createResonanceFeedback, listResonanceItems } from '../../lib/journal'
import type { ResonanceItem } from '../../lib/types'

export default function ResonanceWallPage() {
  const { message } = App.useApp()
  const [items, setItems] = useState<ResonanceItem[]>([])
  const [loading, setLoading] = useState(false)
  const [empathyLoadingId, setEmpathyLoadingId] = useState<number | null>(null)

  const loadItems = useCallback(async () => {
    setLoading(true)
    try {
      setItems(await listResonanceItems())
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '暂时无法读取共振墙。'))
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    void loadItems()
  }, [loadItems])

  const handleEmpathy = async (item: ResonanceItem) => {
    setEmpathyLoadingId(item.id)
    try {
      const feedback = await createResonanceFeedback(item.id)
      setItems((prev) =>
        prev.map((current) =>
          current.id === item.id
            ? {
                ...current,
                empathy_count: feedback.empathy_count,
                has_empathy_feedback: feedback.has_empathy_feedback,
              }
            : current,
        ),
      )
      message.success('已记录共鸣')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '记录失败，请稍后再试。'))
    } finally {
      setEmpathyLoadingId(null)
    }
  }

  return (
    <Flex vertical gap={20}>
      <Flex align="center" justify="space-between" gap={12} wrap="wrap">
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            共振墙
          </Typography.Title>
          <Typography.Text type="secondary">每一条被收录的日记，像一棵微微发光的树。</Typography.Text>
        </Space>
        <Button icon={<ReloadOutlined />} onClick={loadItems} loading={loading}>
          刷新
        </Button>
      </Flex>

      {loading ? (
        <Flex justify="center" style={{ padding: 48 }}>
          <Spin />
        </Flex>
      ) : items.length === 0 ? (
        <Empty description="共振墙还没有收录片段" />
      ) : (
        <div className="resonance-forest">
          {items.map((item) => (
            <Card key={item.id} className="resonance-tree-card">
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                <Typography.Paragraph style={{ margin: 0, fontSize: 16, lineHeight: 1.9 }}>
                  {item.excerpt}
                </Typography.Paragraph>
                <Button
                  icon={<BulbOutlined />}
                  onClick={() => handleEmpathy(item)}
                  loading={empathyLoadingId === item.id}
                  disabled={item.has_empathy_feedback}
                >
                  {item.has_empathy_feedback ? '已共鸣' : '我也共鸣'} · {item.empathy_count}
                </Button>
              </Space>
            </Card>
          ))}
        </div>
      )}
    </Flex>
  )
}
