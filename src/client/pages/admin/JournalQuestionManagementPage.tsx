import { App, Alert, Button, Form, Input, InputNumber, Modal, Popconfirm, Space, Switch, Table, Typography } from 'antd'
import { EditOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { TableColumnsType } from 'antd'
import {
  createDailyQuestion,
  deleteDailyQuestion,
  listDailyQuestions,
  updateDailyQuestion,
} from '../../lib/journal'
import type { DailyQuestion, DailyQuestionPayload } from '../../lib/types'
import { resolveApiErrorMessage } from '../../lib/error'

type QuestionFormValues = DailyQuestionPayload

export default function JournalQuestionManagementPage() {
  const { message } = App.useApp()
  const [questions, setQuestions] = useState<DailyQuestion[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingQuestion, setEditingQuestion] = useState<DailyQuestion | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm<QuestionFormValues>()

  const loadQuestions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listDailyQuestions()
      setQuestions(data)
    } catch (err) {
      const text = resolveApiErrorMessage(err, '暂时无法读取每日问题。')
      setError(text)
      message.error(text)
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    void loadQuestions()
  }, [loadQuestions])

  const openCreateModal = () => {
    setEditingQuestion(null)
    form.setFieldsValue({ content: '', is_active: true, sort_order: 100 })
    setModalOpen(true)
  }

  const openEditModal = useCallback((question: DailyQuestion) => {
    setEditingQuestion(question)
    form.setFieldsValue({
      content: question.content,
      is_active: question.is_active,
      sort_order: question.sort_order,
    })
    setModalOpen(true)
  }, [form])

  const closeModal = () => {
    setModalOpen(false)
    setEditingQuestion(null)
    form.resetFields()
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      if (editingQuestion) {
        const updated = await updateDailyQuestion(editingQuestion.id, values)
        setQuestions((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
        message.success('每日问题已更新')
      } else {
        const created = await createDailyQuestion(values)
        setQuestions((prev) => [...prev, created].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id))
        message.success('每日问题已新增')
      }
      closeModal()
    } catch (err) {
      if (typeof err === 'object' && err && 'errorFields' in err) {
        return
      }
      message.error(resolveApiErrorMessage(err, '保存失败，请稍后再试。'))
    } finally {
      setSaving(false)
    }
  }

  const handleToggleActive = useCallback(async (question: DailyQuestion, isActive: boolean) => {
    try {
      const updated = await updateDailyQuestion(question.id, { is_active: isActive })
      setQuestions((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '更新失败，请稍后再试。'))
    }
  }, [message])

  const handleDelete = useCallback(async (question: DailyQuestion) => {
    try {
      await deleteDailyQuestion(question.id)
      setQuestions((prev) => prev.filter((item) => item.id !== question.id))
      message.success('每日问题已删除')
    } catch (err) {
      message.error(resolveApiErrorMessage(err, '删除失败，请稍后再试。'))
    }
  }, [message])

  const columns: TableColumnsType<DailyQuestion> = useMemo(
    () => [
      {
        title: '问题',
        dataIndex: 'content',
        key: 'content',
        render: (value: string) => <Typography.Text>{value}</Typography.Text>,
      },
      {
        title: '排序',
        dataIndex: 'sort_order',
        key: 'sort_order',
        width: 100,
      },
      {
        title: '启用',
        dataIndex: 'is_active',
        key: 'is_active',
        width: 100,
        render: (value: boolean, record) => (
          <Switch checked={value} onChange={(checked) => handleToggleActive(record, checked)} />
        ),
      },
      {
        title: '更新时间',
        dataIndex: 'updated_at',
        key: 'updated_at',
        render: (value: string) => new Date(value).toLocaleString(),
      },
      {
        title: '操作',
        key: 'actions',
        width: 160,
        render: (_, record) => (
          <Space>
            <Button size="small" icon={<EditOutlined />} onClick={() => openEditModal(record)}>
              编辑
            </Button>
            <Popconfirm
              title="删除每日问题"
              description="已写过的日记仍会保留。"
              onConfirm={() => handleDelete(record)}
              okText="删除"
              cancelText="取消"
            >
              <Button size="small" danger>
                删除
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [handleDelete, handleToggleActive, openEditModal],
  )

  return (
    <Space direction="vertical" size={20} style={{ width: '100%' }}>
      <Space direction="vertical" size={4}>
        <Typography.Title level={4} style={{ margin: 0 }}>
          每日问题
        </Typography.Title>
        <Typography.Text type="secondary">
          启用的问题会按日期顺序轮换，作为用户今日书写的入口。
        </Typography.Text>
      </Space>

      <Space wrap>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
          新增问题
        </Button>
        <Button icon={<ReloadOutlined />} onClick={loadQuestions} loading={loading}>
          刷新
        </Button>
      </Space>

      {error && <Alert type="error" showIcon message={error} />}

      <Table
        columns={columns}
        dataSource={questions}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 'max-content' }}
        locale={{ emptyText: '暂无每日问题' }}
      />

      <Modal
        title={editingQuestion ? '编辑每日问题' : '新增每日问题'}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSave}
        confirmLoading={saving}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" initialValues={{ is_active: true, sort_order: 100 }}>
          <Form.Item
            name="content"
            label="问题内容"
            rules={[{ required: true, whitespace: true, message: '请输入问题内容' }]}
          >
            <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} maxLength={500} showCount />
          </Form.Item>
          <Form.Item name="sort_order" label="排序" rules={[{ required: true, message: '请输入排序' }]}>
            <InputNumber min={0} max={999999} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="is_active" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
