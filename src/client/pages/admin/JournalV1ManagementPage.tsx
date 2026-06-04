import {
  App,
  Alert,
  Button,
  Card,
  Flex,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Statistic,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
} from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { resolveApiErrorMessage } from '../../lib/error'
import {
  createJournalClass,
  createResonanceItem,
  fetchJournalAdminDashboard,
  listAdminAwarenessSessions,
  listJournalClasses,
  regenerateJournalClassCode,
  reviewAwarenessSession,
  updateJournalClass,
} from '../../lib/journal'
import type {
  AdminAwarenessSession,
  JournalAdminDashboard,
  JournalClass,
} from '../../lib/types'

export default function JournalV1ManagementPage() {
  return (
    <Tabs
      items={[
        { key: 'dashboard', label: '数据看板', children: <DashboardTab /> },
        { key: 'classes', label: '班级管理', children: <ClassesTab /> },
        { key: 'review', label: '日记批阅', children: <ReviewTab /> },
      ]}
    />
  )
}

function DashboardTab() {
  const [data, setData] = useState<JournalAdminDashboard | null>(null)
  const [loading, setLoading] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      setData(await fetchJournalAdminDashboard())
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadData()
  }, [loadData])

  return (
    <Flex vertical gap={16}>
      <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading} style={{ width: 120 }}>
        刷新
      </Button>
      <Flex gap={16} wrap="wrap">
        <Metric title="班级数" value={data?.class_count ?? 0} />
        <Metric title="已绑定学生" value={data?.student_count ?? 0} />
        <Metric title="今日提交" value={data?.submitted_today_count ?? 0} />
        <Metric title="提交率" value={`${Math.round((data?.submission_rate ?? 0) * 100)}%`} />
        <Metric title="累计日记" value={data?.total_sessions ?? 0} />
        <Metric title="共振片段" value={data?.resonance_count ?? 0} />
      </Flex>
      <Card title="情绪分布">
        <Space wrap>
          {Object.entries(data?.emotion_counts ?? {}).map(([emotion, count]) => (
            <Tag color="green" key={emotion}>
              {emotion} · {count}
            </Tag>
          ))}
        </Space>
      </Card>
    </Flex>
  )
}

function Metric({ title, value }: { title: string; value: string | number }) {
  return (
    <Card style={{ minWidth: 150 }}>
      <Statistic title={title} value={value} />
    </Card>
  )
}

function ClassesTab() {
  const { message } = App.useApp()
  const [form] = Form.useForm<{ name: string; is_active: boolean }>()
  const [classes, setClasses] = useState<JournalClass[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const loadClasses = useCallback(async () => {
    setLoading(true)
    try {
      setClasses(await listJournalClasses())
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '暂时无法读取班级。'))
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    void loadClasses()
  }, [loadClasses])

  const handleCreate = async (values: { name: string; is_active: boolean }) => {
    setSaving(true)
    try {
      await createJournalClass(values)
      form.resetFields()
      await loadClasses()
      message.success('班级已创建')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '创建失败。'))
    } finally {
      setSaving(false)
    }
  }

  const handleToggle = async (item: JournalClass, isActive: boolean) => {
    await updateJournalClass(item.id, { is_active: isActive })
    await loadClasses()
  }

  const handleRegenerate = async (item: JournalClass) => {
    await regenerateJournalClassCode(item.id)
    await loadClasses()
    message.success('绑定码已重置')
  }

  return (
    <Flex vertical gap={16}>
      <Card title="创建班级">
        <Form
          form={form}
          layout="inline"
          initialValues={{ is_active: true }}
          onFinish={handleCreate}
        >
          <Form.Item name="name" rules={[{ required: true, message: '请输入班级名称' }]}>
            <Input placeholder="班级名称" />
          </Form.Item>
          <Form.Item name="is_active" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={saving}>
            创建
          </Button>
        </Form>
      </Card>
      <Table
        rowKey="id"
        loading={loading}
        dataSource={classes}
        columns={[
          { title: '班级', dataIndex: 'name' },
          { title: '绑定码', dataIndex: 'binding_code' },
          {
            title: '状态',
            render: (_, item) => (
              <Switch checked={item.is_active} onChange={(checked) => handleToggle(item, checked)} />
            ),
          },
          {
            title: '操作',
            render: (_, item) => <Button onClick={() => handleRegenerate(item)}>重置绑定码</Button>,
          },
        ]}
      />
    </Flex>
  )
}

function ReviewTab() {
  const { message } = App.useApp()
  const [classes, setClasses] = useState<JournalClass[]>([])
  const [classId, setClassId] = useState<number>()
  const [sessions, setSessions] = useState<AdminAwarenessSession[]>([])
  const [loading, setLoading] = useState(false)
  const [reviewing, setReviewing] = useState<AdminAwarenessSession | null>(null)
  const [form] = Form.useForm<{ review_comment: string }>()

  const classOptions = useMemo(
    () => classes.map((item) => ({ value: item.id, label: item.name })),
    [classes],
  )

  const loadClasses = useCallback(async () => {
    setClasses(await listJournalClasses())
  }, [])

  const loadSessions = useCallback(async () => {
    setLoading(true)
    try {
      setSessions(await listAdminAwarenessSessions(classId))
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '暂时无法读取日记。'))
    } finally {
      setLoading(false)
    }
  }, [classId, message])

  useEffect(() => {
    void loadClasses()
  }, [loadClasses])

  useEffect(() => {
    void loadSessions()
  }, [loadSessions])

  const openReview = (session: AdminAwarenessSession) => {
    setReviewing(session)
    form.setFieldsValue({
      review_comment: session.review_comment ?? '',
    })
  }

  const handleReview = async () => {
    if (!reviewing) {
      return
    }
    const values = await form.validateFields()
    try {
      await reviewAwarenessSession(reviewing.id, values)
      await loadSessions()
      setReviewing(null)
      message.success('批阅已保存')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '批阅失败。'))
    }
  }

  const handleCollect = async (session: AdminAwarenessSession) => {
    try {
      await createResonanceItem(session.id, { excerpt: null })
      await loadSessions()
      message.success('已匿名收录到共振墙')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '收录失败。'))
    }
  }

  return (
    <Flex vertical gap={16}>
      <Flex gap={12} wrap="wrap">
        <Select
          allowClear
          placeholder="按班级筛选"
          options={classOptions}
          value={classId}
          onChange={setClassId}
          style={{ width: 180 }}
        />
        <Button icon={<ReloadOutlined />} onClick={loadSessions} loading={loading}>
          刷新
        </Button>
      </Flex>
      <Alert type="info" showIcon message="教师批阅只对学生本人可见；共振墙收录会匿名展示片段。" />
      <Table
        rowKey="id"
        loading={loading}
        dataSource={sessions}
        expandable={{
          expandedRowRender: (session) => (
            <Space direction="vertical" size={10} style={{ width: '100%' }}>
              {session.entry_mode === 'free_reflection_v1' ? (
                <AdminFreeReflection session={session} />
              ) : (
                <AdminLegacyAwareness session={session} />
              )}
            </Space>
          ),
        }}
        columns={[
          { title: '日期', dataIndex: 'submitted_on' },
          { title: '学生', render: (_, item) => item.student_name || item.student_username },
          { title: '班级', dataIndex: 'class_name' },
          {
            title: '类型',
            render: (_, item) =>
              item.entry_mode === 'free_reflection_v1' ? '自由书写' : item.emotion_label,
          },
          {
            title: '批阅',
            render: (_, item) =>
              item.reviewed_at ? <Tag color="green">已批阅</Tag> : <Tag>未批阅</Tag>,
          },
          {
            title: '共振墙',
            render: (_, item) =>
              item.is_collected_to_resonance ? <Tag color="cyan">已收录</Tag> : <Tag>未收录</Tag>,
          },
          {
            title: '操作',
            render: (_, item) => (
              <Space>
                <Button onClick={() => openReview(item)}>批阅</Button>
                <Button disabled={item.is_collected_to_resonance} onClick={() => handleCollect(item)}>
                  匿名收录
                </Button>
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title="陪伴式回应"
        open={!!reviewing}
        onCancel={() => setReviewing(null)}
        onOk={handleReview}
        okText="保存"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="review_comment" label="回应">
            <Input.TextArea
              placeholder="写一段陪伴式回应，不打分，不评判。"
              autoSize={{ minRows: 5, maxRows: 10 }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Flex>
  )
}

function AdminFreeReflection({ session }: { session: AdminAwarenessSession }) {
  const topMarks = session.analysis_marks.filter((mark) => mark.is_top)
  return (
    <>
      <Typography.Text type="secondary">原文</Typography.Text>
      <Typography.Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
        {session.free_content}
      </Typography.Paragraph>
      <Typography.Text type="secondary">系统标记</Typography.Text>
      {topMarks.length > 0 ? (
        <Space wrap>
          {topMarks.map((mark) => (
            <Tag key={mark.id} color="gold">
              {mark.word} · {mark.question}
            </Tag>
          ))}
        </Space>
      ) : (
        <Tag color="green">更接近事实观察</Tag>
      )}
      <Typography.Text type="secondary">追问记录</Typography.Text>
      {session.inquiry_records.length > 0 ? (
        <Space direction="vertical" size={8} style={{ width: '100%' }}>
          {session.inquiry_records.map((record) => (
            <Card key={record.mark_id} size="small">
              <Typography.Paragraph style={{ marginBottom: 6 }}>
                {record.question}
              </Typography.Paragraph>
              <Typography.Text>{record.answer || '学生尚未填写答案'}</Typography.Text>
            </Card>
          ))}
        </Space>
      ) : (
        <Typography.Text>学生尚未打开追问。</Typography.Text>
      )}
    </>
  )
}

function AdminLegacyAwareness({ session }: { session: AdminAwarenessSession }) {
  return (
    <>
      <Typography.Text type="secondary">客观记录</Typography.Text>
      {session.objective_events.map((event, index) => (
        <Typography.Paragraph key={index} style={{ margin: 0 }}>
          {index + 1}. {event}
        </Typography.Paragraph>
      ))}
      <Typography.Text type="secondary">情绪标记</Typography.Text>
      <Typography.Paragraph style={{ margin: 0 }}>
        {session.emotion_label} · {session.emotion_note}
      </Typography.Paragraph>
      <Typography.Text type="secondary">当下锚点</Typography.Text>
      <Typography.Paragraph style={{ margin: 0 }}>{session.present_anchor}</Typography.Paragraph>
    </>
  )
}
