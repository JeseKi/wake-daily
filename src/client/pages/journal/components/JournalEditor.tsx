import { Button, Card, Input, Space, Typography } from 'antd'
import { SaveOutlined } from '@ant-design/icons'

interface JournalEditorProps {
  value: string
  saving: boolean
  disabled?: boolean
  onChange: (value: string) => void
  onSave: () => void
}

export default function JournalEditor({ value, saving, disabled, onChange, onSave }: JournalEditorProps) {
  return (
    <Card>
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Typography.Text type="secondary">自由书写</Typography.Text>
        <Input.TextArea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="可以不完整，可以重复，也可以只是写下此刻的一句话。"
          autoSize={{ minRows: 10, maxRows: 18 }}
          disabled={disabled || saving}
          style={{ fontSize: 16, lineHeight: 1.8 }}
        />
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={onSave}
          loading={saving}
          disabled={disabled || !value.trim()}
          size="large"
          block
        >
          保存日记
        </Button>
      </Space>
    </Card>
  )
}

