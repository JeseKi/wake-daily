import { Alert, Card, Skeleton, Space, Typography } from 'antd'
import { QuestionCircleOutlined } from '@ant-design/icons'
import type { DailyQuestion } from '../../../lib/types'

interface DailyQuestionPanelProps {
  question: DailyQuestion | null
  loading: boolean
  error: string | null
}

export default function DailyQuestionPanel({ question, loading, error }: DailyQuestionPanelProps) {
  if (loading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 2 }} />
      </Card>
    )
  }

  if (error) {
    return <Alert type="error" showIcon message={error} />
  }

  return (
    <Card>
      <Space direction="vertical" size={8}>
        <Typography.Text type="secondary">
          <QuestionCircleOutlined /> 今日一问
        </Typography.Text>
        <Typography.Title level={3} style={{ margin: 0, lineHeight: 1.45 }}>
          {question?.content ?? '今天有什么想写下来的？'}
        </Typography.Title>
      </Space>
    </Card>
  )
}

