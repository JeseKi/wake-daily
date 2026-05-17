import {
  Alert,
  App,
  Button,
  Card,
  Space,
  Typography,
} from 'antd'
import { LockOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { resolveApiErrorMessage } from '../../lib/error'

export default function SecurityPage() {
  const {
    user,
    sendPasswordChangeLink,
  } = useAuth()
  const { message } = App.useApp()

  const [passwordSending, setPasswordSending] = useState(false)
  const [passwordCountdown, setPasswordCountdown] = useState(0)
  const [passwordHint, setPasswordHint] = useState<string | null>(null)

  useEffect(() => {
    if (passwordCountdown <= 0) {
      return
    }

    const timer = window.setInterval(() => {
      setPasswordCountdown((prev) => (prev <= 1 ? 0 : prev - 1))
    }, 1000)

    return () => window.clearInterval(timer)
  }, [passwordCountdown])

  const handleSendPasswordLink = async () => {
    if (passwordSending || passwordCountdown > 0) {
      return
    }

    setPasswordSending(true)
    setPasswordHint(null)
    try {
      await sendPasswordChangeLink()
      setPasswordCountdown(60)
      setPasswordHint('确认链接已发送到当前邮箱，请打开邮件中的页面设置新密码。')
      message.success('确认链接已发送')
    } catch (error) {
      const text = resolveApiErrorMessage(error, '确认链接发送失败，请稍后重试。')
      setPasswordHint(text)
      message.error(text)
    } finally {
      setPasswordSending(false)
    }
  }

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card title="密码修改" bordered={false}>
        <Space direction="vertical" size={24} style={{ width: '100%' }}>
          <Typography.Text type="secondary">
            系统会向当前邮箱发送一个确认链接。打开该页面后，才能设置新的登录密码。
          </Typography.Text>
          <Space align="center" size={16}>
            <Typography.Text type="secondary">确认邮件发送至</Typography.Text>
            <Typography.Text strong>{user?.email ?? '-'}</Typography.Text>
          </Space>
          <Button
            type="primary"
            icon={<LockOutlined />}
            loading={passwordSending}
            disabled={passwordCountdown > 0}
            onClick={() => void handleSendPasswordLink()}
            size="large"
          >
            {passwordCountdown > 0 ? `${passwordCountdown}s 后可重发` : '发送确认链接'}
          </Button>
          {passwordHint && <Alert type="info" showIcon message={passwordHint} />}
        </Space>
      </Card>
    </Space>
  )
}

