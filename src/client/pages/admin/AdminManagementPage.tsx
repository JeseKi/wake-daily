import { KeyOutlined, LockOutlined, QuestionCircleOutlined, TeamOutlined } from '@ant-design/icons'
import { Tabs } from 'antd'
import UserManagementPage from './UserManagementPage'
import PermissionManagementPage from './PermissionManagementPage'
import ScopeManagementPage from './ScopeManagementPage'
import JournalQuestionManagementPage from './JournalQuestionManagementPage'

const tabItems = [
  {
    key: 'users',
    label: (
      <span>
        <TeamOutlined />
        用户管理
      </span>
    ),
    children: <UserManagementPage />,
  },
  {
    key: 'journal-questions',
    label: (
      <span>
        <QuestionCircleOutlined />
        每日问题
      </span>
    ),
    children: <JournalQuestionManagementPage />,
  },
  {
    key: 'scopes',
    label: (
      <span>
        <LockOutlined />
        Scope 管理
      </span>
    ),
    children: <ScopeManagementPage />,
  },
  {
    key: 'permissions',
    label: (
      <span>
        <KeyOutlined />
        权限管理
      </span>
    ),
    children: <PermissionManagementPage />,
  },
]

export default function AdminManagementPage() {
  return (
    <div style={{ overflowX: 'auto' }}>
      <Tabs defaultActiveKey="users" items={tabItems} style={{ minWidth: 500 }} />
    </div>
  )
}
