import { Card, Space, Typography, theme } from 'antd'
import type { ReactNode } from 'react'
import type { AttachmentMatch, JournalEntry } from '../../../lib/types'

interface ReflectionPreviewProps {
  entry: JournalEntry
}

function renderHighlightedContent(content: string, matches: AttachmentMatch[]) {
  const normalizedMatches = [...matches].sort((a, b) => a.start - b.start)
  const nodes: ReactNode[] = []
  let cursor = 0

  normalizedMatches.forEach((match, index) => {
    if (match.start < cursor) {
      return
    }
    if (match.start > cursor) {
      nodes.push(content.slice(cursor, match.start))
    }
    nodes.push(
      <mark key={`${match.word}-${match.start}-${index}`} className="rounded px-1 bg-amber-200/80 text-inherit">
        {content.slice(match.start, match.end)}
      </mark>,
    )
    cursor = match.end
  })

  if (cursor < content.length) {
    nodes.push(content.slice(cursor))
  }

  return nodes
}

export default function ReflectionPreview({ entry }: ReflectionPreviewProps) {
  const { token } = theme.useToken()

  return (
    <Card>
      <Space direction="vertical" size={12} style={{ width: '100%' }}>
        <Typography.Text type="secondary">
          {new Date(entry.created_at).toLocaleString()}
        </Typography.Text>
        <Typography.Text strong>{entry.question_content}</Typography.Text>
        <Typography.Paragraph
          style={{
            margin: 0,
            whiteSpace: 'pre-wrap',
            lineHeight: 1.8,
            color: token.colorText,
          }}
        >
          {renderHighlightedContent(entry.content, entry.attachment_matches)}
        </Typography.Paragraph>
      </Space>
    </Card>
  )
}
