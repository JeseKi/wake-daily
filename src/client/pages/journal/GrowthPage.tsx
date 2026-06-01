import { Alert, Card, Empty, Flex, Progress, Space, Spin, Tag, Typography } from 'antd'
import { useCallback, useEffect, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import { fetchGrowth } from '../../lib/journal'
import type { Growth } from '../../lib/types'

const stageProgress: Record<string, number> = {
  种子: 8,
  幼苗: 24,
  小树: 48,
  大树: 76,
  开花: 100,
}

const stageSymbol: Record<string, string> = {
  种子: '·',
  幼苗: '♧',
  小树: '♧',
  大树: '♣',
  开花: '✦',
}

export default function GrowthPage() {
  const [growth, setGrowth] = useState<Growth | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadGrowth = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setGrowth(await fetchGrowth())
    } catch (err) {
      setError(resolveApiErrorMessage(err, '暂时无法读取成长记录。'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadGrowth()
  }, [loadGrowth])

  return (
    <Flex vertical gap={20}>
      <Space direction="vertical" size={4}>
        <Typography.Title level={2} style={{ margin: 0 }}>
          我的成长
        </Typography.Title>
        <Typography.Text type="secondary">无声生长，不排名，也不催促。</Typography.Text>
      </Space>

      {error && <Alert type="error" showIcon message={error} />}

      {loading ? (
        <Flex justify="center" style={{ padding: 48 }}>
          <Spin />
        </Flex>
      ) : growth ? (
        <Card className="forest-card growth-tree-card">
          <Flex vertical gap={18} align="center">
            <div className="growth-tree-stage">
              {stageSymbol[growth.tree_stage] ?? '·'}
            </div>
            <Typography.Title level={3} style={{ margin: 0 }}>
              {growth.tree_stage}
            </Typography.Title>
            <Typography.Text type="secondary">
              连续 {growth.streak_days} 天 · 累计 {growth.total_sessions} 次觉察
            </Typography.Text>
            <Progress
              percent={stageProgress[growth.tree_stage] ?? 0}
              showInfo={false}
              strokeColor="#61725f"
              trailColor="#e7eee8"
              style={{ maxWidth: 520 }}
            />
            {growth.badges.length > 0 ? (
              <Space wrap>
                {growth.badges.map((badge) => (
                  <Tag color="green" key={badge}>
                    {badge}
                  </Tag>
                ))}
              </Space>
            ) : (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="还没有徽章" />
            )}
          </Flex>
        </Card>
      ) : null}
    </Flex>
  )
}
