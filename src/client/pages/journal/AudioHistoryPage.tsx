import { Alert, Card, Empty, Flex, Space, Spin, Tag, Typography } from 'antd'
import { CustomerServiceOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import { GUIDED_AUDIO_LIST } from '../../lib/guidedAudio'
import { fetchGrowth } from '../../lib/journal'
import type { Growth } from '../../lib/types'

export default function AudioHistoryPage() {
  const [growth, setGrowth] = useState<Growth | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadGrowth = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setGrowth(await fetchGrowth())
    } catch (err) {
      setError(resolveApiErrorMessage(err, '暂时无法读取语音历史。'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadGrowth()
  }, [loadGrowth])

  const unlockedAudios = useMemo(() => {
    return GUIDED_AUDIO_LIST.slice(0, growth?.unlocked_guided_audio_days ?? 0)
  }, [growth?.unlocked_guided_audio_days])

  return (
    <Flex vertical gap={20}>
      <Flex align="center" justify="space-between" gap={12} wrap="wrap">
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            语音历史
          </Typography.Title>
          <Typography.Text type="secondary">已经打开过的引导，都会留在这里。</Typography.Text>
        </Space>
        {growth && (
          <Tag color="green">
            已解锁 {growth.unlocked_guided_audio_days}/7
          </Tag>
        )}
      </Flex>

      {error && <Alert type="error" showIcon message={error} />}

      {loading ? (
        <Flex justify="center" style={{ padding: 48 }}>
          <Spin />
        </Flex>
      ) : !growth ? null : unlockedAudios.length === 0 ? (
        <Empty description="还没有已解锁语音" />
      ) : (
        <Flex vertical gap={16}>
          {unlockedAudios.map((audio) => (
            <Card key={audio.day} className="forest-card">
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Flex align="center" justify="space-between" gap={12} wrap="wrap">
                  <Space size={10}>
                    <CustomerServiceOutlined />
                    <Typography.Text strong>{audio.label}</Typography.Text>
                  </Space>
                  <Tag color={audio.url ? 'green' : 'default'}>
                    {audio.url ? '可回听' : '准备中'}
                  </Tag>
                </Flex>
                {audio.url ? (
                  <audio
                    className="guided-audio-player"
                    controls
                    preload="metadata"
                    src={audio.url}
                  >
                    您的浏览器暂不支持音频播放。
                  </audio>
                ) : (
                  <Alert type="info" showIcon message="这段引导语音准备中" />
                )}
              </Space>
            </Card>
          ))}
        </Flex>
      )}
    </Flex>
  )
}
