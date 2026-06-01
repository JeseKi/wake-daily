import {
  App,
  Alert,
  Button,
  Card,
  Checkbox,
  Flex,
  Input,
  Radio,
  Select,
  Space,
  Steps,
  Tag,
  Typography,
} from 'antd'
import { AudioMutedOutlined, SoundOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { resolveApiErrorMessage } from '../../lib/error'
import {
  bindJournalClass,
  createAwarenessSession,
  fetchMyJournalBinding,
} from '../../lib/journal'
import type { AwarenessSession, JournalBinding, ObjectivityWarning } from '../../lib/types'

const subjectiveWords = [
  '觉得',
  '想',
  '认为',
  '无聊',
  '开心',
  '难过',
  '烦躁',
  '感觉',
  '总是',
  '肯定',
  '担心',
  '害怕',
  '希望',
  '讨厌',
  '喜欢',
  '竟然',
  '不负责任',
  '莫名其妙',
]

const emotionOptions = [
  '平静',
  '开心',
  '难过',
  '生气',
  '害怕',
  '焦虑',
  '委屈',
  '羞愧',
  '期待',
  '困惑',
].map((value) => ({ value, label: value }))

const voiceStorageKey = 'wake-daily-guide-voice-enabled'

function detectObjectivity(events: string[]): ObjectivityWarning[] {
  return events.flatMap((event, eventIndex) => {
    const warnings: ObjectivityWarning[] = []
    if (event.includes('我')) {
      warnings.push({
        event_index: eventIndex,
        word: '我',
        message: '请尝试使用第三人称视角，避免使用“我”。',
      })
    }
    subjectiveWords.forEach((word) => {
      if (event.includes(word)) {
        warnings.push({
          event_index: eventIndex,
          word,
          message: `检测到主观词“${word}”，请确认是否在描述事实。`,
        })
      }
    })
    return warnings
  })
}

function speakGuide(text: string, enabled: boolean) {
  if (!enabled || typeof window === 'undefined' || !window.speechSynthesis) {
    return
  }
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'zh-CN'
  utterance.rate = 0.86
  utterance.pitch = 0.95
  window.speechSynthesis.speak(utterance)
  window.setTimeout(() => window.speechSynthesis.cancel(), 15000)
}

export default function TodayJournalPage() {
  const { message } = App.useApp()
  const [binding, setBinding] = useState<JournalBinding | null>(null)
  const [bindingCode, setBindingCode] = useState('')
  const [loadingBinding, setLoadingBinding] = useState(false)
  const [bindingSubmitting, setBindingSubmitting] = useState(false)
  const [step, setStep] = useState(0)
  const [events, setEvents] = useState(['', '', ''])
  const [selectedEventIndex, setSelectedEventIndex] = useState(0)
  const [emotionLabel, setEmotionLabel] = useState<string>()
  const [emotionNote, setEmotionNote] = useState('')
  const [presentAnchor, setPresentAnchor] = useState('')
  const [saving, setSaving] = useState(false)
  const [savedSession, setSavedSession] = useState<AwarenessSession | null>(null)
  const [voiceEnabled, setVoiceEnabled] = useState(() => {
    return window.localStorage.getItem(voiceStorageKey) !== 'false'
  })

  const objectiveEvents = useMemo(
    () => events.map((item) => item.trim()).filter(Boolean),
    [events],
  )
  const warnings = useMemo(() => detectObjectivity(objectiveEvents), [objectiveEvents])
  const selectedEvent = objectiveEvents[selectedEventIndex] ?? objectiveEvents[0] ?? ''

  const loadBinding = useCallback(async () => {
    setLoadingBinding(true)
    try {
      setBinding(await fetchMyJournalBinding())
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '暂时无法读取班级绑定。'))
    } finally {
      setLoadingBinding(false)
    }
  }, [message])

  useEffect(() => {
    void loadBinding()
  }, [loadBinding])

  useEffect(() => {
    window.localStorage.setItem(voiceStorageKey, String(voiceEnabled))
  }, [voiceEnabled])

  const handleBind = async () => {
    if (!bindingCode.trim()) {
      return
    }
    setBindingSubmitting(true)
    try {
      const data = await bindJournalClass(bindingCode)
      setBinding(data)
      message.success('已绑定班级')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '绑定失败，请检查绑定码。'))
    } finally {
      setBindingSubmitting(false)
    }
  }

  const handleNext = () => {
    const guideTexts = [
      '回顾刚才记录的事，哪一件触发了你最大的情绪波动？',
      '暂停片刻，像水面一样，映照此刻。',
    ]
    if (step < 2) {
      speakGuide(guideTexts[step], voiceEnabled)
      setStep(step + 1)
    }
  }

  const handleSave = async () => {
    if (!emotionLabel || !selectedEvent || !emotionNote.trim() || !presentAnchor.trim()) {
      return
    }

    setSaving(true)
    try {
      const session = await createAwarenessSession({
        objective_events: objectiveEvents,
        selected_event_index: selectedEventIndex,
        emotion_label: emotionLabel,
        emotion_note: emotionNote,
        present_anchor: presentAnchor,
      })
      setSavedSession(session)
      message.success('今日觉察已保存')
    } catch (error) {
      message.error(resolveApiErrorMessage(error, '保存失败，请稍后再试。'))
    } finally {
      setSaving(false)
    }
  }

  if (!binding?.is_bound) {
    return (
      <Flex vertical gap={20}>
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            进入觉察日记
          </Typography.Title>
          <Typography.Text type="secondary">输入教师下发的绑定码，进入自己的林间空地。</Typography.Text>
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
      <Flex align="center" justify="space-between" gap={12} wrap="wrap">
        <Space direction="vertical" size={4}>
          <Typography.Title level={2} style={{ margin: 0 }}>
            今日觉察
          </Typography.Title>
          <Typography.Text type="secondary">
            {binding.class_info?.name} · 像照相机，也像水面。
          </Typography.Text>
        </Space>
        <Checkbox checked={voiceEnabled} onChange={(event) => setVoiceEnabled(event.target.checked)}>
          {voiceEnabled ? <SoundOutlined /> : <AudioMutedOutlined />} 引导语音
        </Checkbox>
      </Flex>

      <Steps
        current={step}
        items={[
          { title: '客观记录' },
          { title: '情绪标记' },
          { title: '当下锚点' },
        ]}
      />

      {step === 0 && (
        <Card className="forest-card water-surface-card">
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Typography.Text strong>请站在第三人称视角，像照相机一样，只记录今天发生的 1-3 件事。</Typography.Text>
            {events.map((value, index) => (
              <Input.TextArea
                key={index}
                value={value}
                onChange={(event) => {
                  const next = [...events]
                  next[index] = event.target.value
                  setEvents(next)
                }}
                placeholder={`事件 ${index + 1}`}
                autoSize={{ minRows: 2, maxRows: 4 }}
              />
            ))}
            {warnings.length > 0 && (
              <Alert
                type="info"
                showIcon
                message="客观性提醒"
                description={
                  <Space direction="vertical" size={4}>
                    {warnings.map((warning, index) => (
                      <Typography.Text key={`${warning.event_index}-${warning.word}-${index}`}>
                        事件 {warning.event_index + 1}：{warning.message}
                      </Typography.Text>
                    ))}
                  </Space>
                }
              />
            )}
            <Button type="primary" size="large" onClick={handleNext} disabled={objectiveEvents.length === 0}>
              进入第二关
            </Button>
          </Space>
        </Card>
      )}

      {step === 1 && (
        <Card className="forest-card">
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Typography.Text strong>回顾刚才记录的事，哪一件触发了你最大的情绪波动？</Typography.Text>
            <Radio.Group
              value={selectedEventIndex}
              onChange={(event) => setSelectedEventIndex(event.target.value)}
            >
              <Space direction="vertical">
                {objectiveEvents.map((event, index) => (
                  <Radio key={index} value={index}>
                    {event}
                  </Radio>
                ))}
              </Space>
            </Radio.Group>
            <Select
              value={emotionLabel}
              options={emotionOptions}
              onChange={setEmotionLabel}
              placeholder="选择一个情绪词"
              size="large"
            />
            <Input.TextArea
              value={emotionNote}
              onChange={(event) => setEmotionNote(event.target.value)}
              placeholder="简短写下触发点。"
              autoSize={{ minRows: 4, maxRows: 8 }}
            />
            <Flex gap={12} wrap="wrap">
              <Button onClick={() => setStep(0)}>返回第一关</Button>
              <Button
                type="primary"
                onClick={handleNext}
                disabled={!emotionLabel || !emotionNote.trim()}
              >
                进入第三关
              </Button>
            </Flex>
          </Space>
        </Card>
      )}

      {step === 2 && (
        <Card className="forest-card water-surface-card">
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Typography.Text strong>暂停片刻，观察周围环境，记录一个之前忽略的细节。</Typography.Text>
            <Tag color="cyan">像水面一样，映照此刻</Tag>
            <Input.TextArea
              value={presentAnchor}
              onChange={(event) => setPresentAnchor(event.target.value)}
              placeholder="例如：窗边有一小块光，桌面比刚才凉一点。"
              autoSize={{ minRows: 5, maxRows: 10 }}
            />
            <Flex gap={12} wrap="wrap">
              <Button onClick={() => setStep(1)}>返回第二关</Button>
              <Button
                type="primary"
                loading={saving}
                disabled={!presentAnchor.trim() || !!savedSession}
                onClick={handleSave}
              >
                保存今日觉察
              </Button>
            </Flex>
          </Space>
        </Card>
      )}

      {savedSession && (
        <Alert
          type="success"
          showIcon
          message="这棵小树已经种下。"
          description={<Link to="/journal/recent">查看我的觉察本</Link>}
        />
      )}
    </Flex>
  )
}
