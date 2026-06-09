import {
  App,
  Alert,
  Button,
  Card,
  Collapse,
  Flex,
  Input,
  Space,
  Spin,
  Tag,
  Tooltip,
  Typography,
} from 'antd'
import {
  EditOutlined,
  PlayCircleOutlined,
  QuestionCircleOutlined,
  SaveOutlined,
} from '@ant-design/icons'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { resolveApiErrorMessage } from '../../lib/error'
import { GUIDED_AUDIO_BY_DAY } from '../../lib/guidedAudio'
import {
  bindJournalClass,
  createAwarenessSession,
  fetchGrowth,
  fetchMyJournalBinding,
  fetchTodayAwarenessSession,
  updateAwarenessSessionInquiries,
} from '../../lib/journal'
import type {
  AnalysisMark,
  AwarenessSession,
  InquiryRecord,
  JournalBinding,
  ObjectiveSegment,
} from '../../lib/types'

export default function TodayJournalPage() {
  const { message } = App.useApp()
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [binding, setBinding] = useState<JournalBinding | null>(null)
  const [bindingCode, setBindingCode] = useState('')
  const [loadingBinding, setLoadingBinding] = useState(false)
  const [bindingSubmitting, setBindingSubmitting] = useState(false)
  const [hasEnteredWriting, setHasEnteredWriting] = useState(false)
  const [audioLoading, setAudioLoading] = useState(false)
  const [growthLoading, setGrowthLoading] = useState(false)
  const [todaySessionLoading, setTodaySessionLoading] = useState(false)
  const [streakDays, setStreakDays] = useState<number | null>(null)
  const [content, setContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [savedSession, setSavedSession] = useState<AwarenessSession | null>(null)
  const [isEditingSavedSession, setIsEditingSavedSession] = useState(false)
  const [inquirySaving, setInquirySaving] = useState(false)

  const guidedAudioDay = streakDays === null ? null : (streakDays % 7) + 1
  const guidedAudio = guidedAudioDay === null ? null : GUIDED_AUDIO_BY_DAY[guidedAudioDay]

  const topMarks = useMemo(
    () => savedSession?.analysis_marks.filter((mark) => mark.is_top).slice(0, 3) ?? [],
    [savedSession],
  )
  const foldedMarks = useMemo(
    () => savedSession?.analysis_marks.filter((mark) => !mark.is_top) ?? [],
    [savedSession],
  )
  const recordsByMarkId = useMemo(() => {
    return new Map((savedSession?.inquiry_records ?? []).map((record) => [record.mark_id, record]))
  }, [savedSession])

  const loadGrowth = useCallback(async () => {
    setGrowthLoading(true)
    try {
      const growth = await fetchGrowth()
      setStreakDays(growth.streak_days)
    } catch (error) {
      setStreakDays(0)
      message.error(resolveApiErrorMessage(error, '暂时无法读取连续天数，先使用第一天引导语音。'))
    } finally {
      setGrowthLoading(false)
    }
  }, [message])

  const loadTodaySession = useCallback(async () => {
    setTodaySessionLoading(true)
    try {
      const session = await fetchTodayAwarenessSession()
      setSavedSession(session)
      setIsEditingSavedSession(false)
      if (session?.free_content) {
        setContent(session.free_content)
        setHasEnteredWriting(true)
      }
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '暂时无法读取今日书写。'))
    } finally {
      setTodaySessionLoading(false)
    }
  }, [message])

  const loadBinding = useCallback(async () => {
    setLoadingBinding(true)
    try {
      const data = await fetchMyJournalBinding()
      setBinding(data)
      if (data.is_bound) {
        void loadGrowth()
        void loadTodaySession()
      }
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '暂时无法读取班级绑定。'))
    } finally {
      setLoadingBinding(false)
    }
  }, [loadGrowth, loadTodaySession, message])

  useEffect(() => {
    void loadBinding()
  }, [loadBinding])

  useEffect(() => {
    setAudioLoading(!!guidedAudio?.url)
  }, [guidedAudio?.url])

  const handleBind = async () => {
    if (!bindingCode.trim()) {
      return
    }
    setBindingSubmitting(true)
    try {
      const data = await bindJournalClass(bindingCode)
      setBinding(data)
      void loadGrowth()
      void loadTodaySession()
      message.success('已绑定班级')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '绑定失败，请检查绑定码。'))
    } finally {
      setBindingSubmitting(false)
    }
  }

  const handleEnterWriting = async () => {
    setHasEnteredWriting(true)
    if (!guidedAudio?.url) {
      return
    }
    try {
      await audioRef.current?.play()
    } catch {
      message.info('如未自动播放，请点击播放条开始引导语音。')
    }
  }

  const handleSave = async () => {
    if (!content.trim()) {
      return
    }
    setSaving(true)
    try {
      const session = await createAwarenessSession({ content })
      setSavedSession(session)
      setContent(session.free_content ?? content)
      setHasEnteredWriting(true)
      setIsEditingSavedSession(false)
      message.success(savedSession ? '今日书写已更新' : '今日书写已保存')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '保存失败，请稍后再试。'))
    } finally {
      setSaving(false)
    }
  }

  const handleOpenInquiry = async (mark: AnalysisMark) => {
    if (!savedSession || recordsByMarkId.has(mark.id)) {
      return
    }
    const nextRecords = [
      ...savedSession.inquiry_records,
      {
        mark_id: mark.id,
        question: mark.question,
        opened_at: new Date().toISOString(),
        answer: null,
        updated_at: null,
      },
    ]
    await persistInquiryRecords(nextRecords)
  }

  const handleAnswerChange = async (record: InquiryRecord, answer: string) => {
    if (!savedSession) {
      return
    }
    const nextRecords = savedSession.inquiry_records.map((item) =>
      item.mark_id === record.mark_id
        ? { ...item, answer, updated_at: new Date().toISOString() }
        : item,
    )
    await persistInquiryRecords(nextRecords)
  }

  const persistInquiryRecords = async (records: InquiryRecord[]) => {
    if (!savedSession) {
      return
    }
    setInquirySaving(true)
    try {
      setSavedSession(await updateAwarenessSessionInquiries(savedSession.id, records))
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '追问记录保存失败。'))
    } finally {
      setInquirySaving(false)
    }
  }

  if (!binding?.is_bound) {
    return (
      <Flex vertical gap={20}>
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            进入觉察日记
          </Typography.Title>
          <Typography.Text type="secondary">输入教师下发的绑定码，进入自己的书写空间。</Typography.Text>
        </Space>
        <Card loading={loadingBinding} className="forest-card">
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Input
              value={bindingCode}
              onChange={(event) => setBindingCode(event.target.value.toUpperCase())}
              placeholder="班级绑定码"
              size="large"
              maxLength={32}
            />
            <Button
              type="primary"
              size="large"
              block
              onClick={handleBind}
              loading={bindingSubmitting}
              disabled={!bindingCode.trim()}
            >
              绑定班级
            </Button>
          </Space>
        </Card>
      </Flex>
    )
  }

  return (
    <Flex vertical gap={20}>
      <Space direction="vertical" size={4}>
        <Typography.Title level={2} style={{ margin: 0 }}>
          今日书写
        </Typography.Title>
        <Typography.Text type="secondary">{binding.class_info?.name}</Typography.Text>
      </Space>

      {!savedSession ? (
        <Card className="forest-card free-writing-card" loading={todaySessionLoading}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <div className="guided-audio-panel">
              <Flex align="center" justify="space-between" gap={12}>
                <Typography.Text strong>引导语音</Typography.Text>
                {(growthLoading || audioLoading) && (
                  <Space size={6}>
                    <Spin size="small" />
                    <Typography.Text type="secondary">
                      {growthLoading ? '正在匹配' : '正在加载'}
                    </Typography.Text>
                  </Space>
                )}
              </Flex>
              {guidedAudio?.url ? (
                <>
                  <Typography.Text type="secondary">{guidedAudio.label}</Typography.Text>
                  <audio
                    ref={audioRef}
                    className="guided-audio-player"
                    controls
                    preload="metadata"
                    src={guidedAudio.url}
                    onLoadStart={() => setAudioLoading(true)}
                    onLoadedMetadata={() => setAudioLoading(false)}
                    onCanPlay={() => setAudioLoading(false)}
                    onPlaying={() => setAudioLoading(false)}
                    onWaiting={() => setAudioLoading(true)}
                    onError={() => setAudioLoading(false)}
                  >
                    您的浏览器暂不支持音频播放。
                  </audio>
                </>
              ) : (
                <div className="guided-audio-placeholder">
                  <Typography.Text type="secondary">
                    {guidedAudio?.label ?? '引导语音匹配中'}
                  </Typography.Text>
                </div>
              )}
            </div>
            {!hasEnteredWriting ? (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                size="large"
                onClick={handleEnterWriting}
                loading={growthLoading}
              >
                进入书写
              </Button>
            ) : (
              <>
                <Input.TextArea
                  value={content}
                  onChange={(event) => setContent(event.target.value)}
                  placeholder="想写什么就写什么。可以不完整，可以重复，也可以只是此刻的一句话。"
                  autoSize={{ minRows: 14, maxRows: 24 }}
                  disabled={saving}
                  style={{ fontSize: 16, lineHeight: 1.9 }}
                />
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  size="large"
                  onClick={handleSave}
                  loading={saving}
                  disabled={!content.trim()}
                >
                  提交
                </Button>
              </>
            )}
          </Space>
        </Card>
      ) : (
        <Flex vertical gap={16}>
          <Card className="forest-card">
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <Flex align="center" justify="space-between" gap={12} wrap="wrap">
                <Typography.Text type="secondary">系统标记</Typography.Text>
                <Button
                  icon={<EditOutlined />}
                  onClick={() => {
                    setContent(savedSession.free_content ?? '')
                    setIsEditingSavedSession(true)
                  }}
                  disabled={saving}
                >
                  编辑今日书写
                </Button>
              </Flex>
              {isEditingSavedSession && (
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <Input.TextArea
                    value={content}
                    onChange={(event) => setContent(event.target.value)}
                    placeholder="想写什么就写什么。可以不完整，可以重复，也可以只是此刻的一句话。"
                    autoSize={{ minRows: 10, maxRows: 20 }}
                    disabled={saving}
                    style={{ fontSize: 16, lineHeight: 1.9 }}
                  />
                  <Space wrap>
                    <Button
                      onClick={() => {
                        setContent(savedSession.free_content ?? '')
                        setIsEditingSavedSession(false)
                      }}
                      disabled={saving}
                    >
                      取消
                    </Button>
                    <Button
                      type="primary"
                      icon={<SaveOutlined />}
                      onClick={handleSave}
                      loading={saving}
                      disabled={!content.trim()}
                    >
                      保存修改
                    </Button>
                  </Space>
                </Space>
              )}
              <Typography.Paragraph style={{ whiteSpace: 'pre-wrap', lineHeight: 1.9, margin: 0 }}>
                {renderMarkedContent(savedSession.free_content ?? '', topMarks)}
              </Typography.Paragraph>
              {topMarks.length > 0 ? (
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  {topMarks.map((mark) => (
                    <MarkInquiry
                      key={mark.id}
                      mark={mark}
                      record={recordsByMarkId.get(mark.id)}
                      saving={inquirySaving}
                      onOpen={() => handleOpenInquiry(mark)}
                      onAnswerChange={(record, answer) => handleAnswerChange(record, answer)}
                    />
                  ))}
                </Space>
              ) : (
                <Alert
                  type="success"
                  showIcon
                  message="这段书写更接近事实观察，写得很清楚。"
                />
              )}
              {savedSession.objective_segments.map((segment) => (
                <ObjectiveSegmentNote key={`${segment.start}-${segment.end}`} segment={segment} />
              ))}
              {foldedMarks.length > 0 && (
                <Collapse
                  ghost
                  items={[
                    {
                      key: 'folded',
                      label: `更多标记 ${foldedMarks.length} 处`,
                      children: (
                        <Space wrap>
                          {foldedMarks.map((mark) => (
                            <Tag key={mark.id} color="gold">
                              {mark.word}
                            </Tag>
                          ))}
                        </Space>
                      ),
                    },
                  ]}
                />
              )}
            </Space>
          </Card>
          <Alert
            type="success"
            showIcon
            message="今日书写已保存。"
            description={<Link to="/journal/recent">查看我的觉察本</Link>}
          />
        </Flex>
      )}
    </Flex>
  )
}

function renderMarkedContent(content: string, marks: AnalysisMark[]) {
  const sortedMarks = [...marks].sort((a, b) => a.start - b.start)
  const nodes: ReactNode[] = []
  let cursor = 0
  sortedMarks.forEach((mark) => {
    if (mark.start < cursor) {
      return
    }
    if (mark.start > cursor) {
      nodes.push(content.slice(cursor, mark.start))
    }
    nodes.push(
      <mark key={mark.id} className="free-writing-mark">
        {content.slice(mark.start, mark.end)}
      </mark>,
    )
    cursor = mark.end
  })
  if (cursor < content.length) {
    nodes.push(content.slice(cursor))
  }
  return nodes
}

function MarkInquiry({
  mark,
  record,
  saving,
  onOpen,
  onAnswerChange,
}: {
  mark: AnalysisMark
  record?: InquiryRecord
  saving: boolean
  onOpen: () => void
  onAnswerChange: (record: InquiryRecord, answer: string) => void | Promise<void>
}) {
  const [localAnswer, setLocalAnswer] = useState(record?.answer ?? '')

  useEffect(() => {
    setLocalAnswer(record?.answer ?? '')
  }, [record?.answer])

  const handleBlur = () => {
    if (!record || localAnswer === (record.answer ?? '')) {
      return
    }
    void onAnswerChange(record, localAnswer)
  }

  return (
    <Card size="small" className="mark-inquiry-card">
      <Space direction="vertical" size={10} style={{ width: '100%' }}>
        <Flex align="center" justify="space-between" gap={12} wrap="wrap">
          <Space>
            <Tag color="gold">{mark.word}</Tag>
            <Typography.Text type="secondary">{mark.question}</Typography.Text>
          </Space>
          <Tooltip title="打开追问">
            <Button
              shape="circle"
              icon={<QuestionCircleOutlined />}
              onClick={onOpen}
              disabled={!!record || saving}
            />
          </Tooltip>
        </Flex>
        {record && (
          <Input.TextArea
            value={localAnswer}
            onChange={(event) => setLocalAnswer(event.target.value)}
            onBlur={handleBlur}
            placeholder="更深一层，我真正想要的是……"
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={saving}
          />
        )}
      </Space>
    </Card>
  )
}

function ObjectiveSegmentNote({ segment }: { segment: ObjectiveSegment }) {
  return (
    <Alert
      type="success"
      showIcon
      message={segment.text}
      description={segment.message}
    />
  )
}
