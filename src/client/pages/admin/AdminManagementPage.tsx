import { KeyOutlined, LockOutlined, ProfileOutlined, QuestionCircleOutlined, TeamOutlined } from '@ant-design/icons'
import { Tabs } from 'antd'
import UserManagementPage from './UserManagementPage'
import PermissionManagementPage from './PermissionManagementPage'
import ScopeManagementPage from './ScopeManagementPage'
import JournalQuestionManagementPage from './JournalQuestionManagementPage'
import JournalV1ManagementPage from './JournalV1ManagementPage'

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
    key: 'journal-v1',
    label: (
      <span>
        <ProfileOutlined />
        觉察日记
      </span>
    ),
    children: <JournalV1ManagementPage />,
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
