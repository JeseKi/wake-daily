import { Button } from 'antd'
import { HeartOutlined } from '@ant-design/icons'

interface ReliefButtonProps {
  loading: boolean
  disabled?: boolean
  hasFeedback?: boolean
  reliefCount?: number
  onClick: () => void
}

export default function ReliefButton({
  loading,
  disabled,
  hasFeedback,
  reliefCount = 0,
  onClick,
}: ReliefButtonProps) {
  return (
    <Button
      icon={<HeartOutlined />}
      loading={loading}
      disabled={disabled || hasFeedback}
      onClick={onClick}
    >
      {hasFeedback ? '已经松了一点' : '这个觉察让我松了一点'}
      {reliefCount > 0 ? ` · ${reliefCount}` : ''}
    </Button>
  )
}

