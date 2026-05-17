import { Button, Dropdown, Avatar, Flex, Typography } from 'antd'
import { LogIn, LogOut, PenLine, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { MenuProps } from 'antd'
import { useAuth } from '../../hooks/useAuth'

export default function LandingPage() {
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    navigate('/', { replace: true })
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'user',
      label: (
        <Flex vertical gap={2} style={{ minWidth: 160 }}>
          <Typography.Text type="secondary">当前用户</Typography.Text>
          <Typography.Text strong>{user?.username ?? '未登录'}</Typography.Text>
        </Flex>
      ),
      disabled: true,
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogOut size={16} />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <main className="min-h-screen bg-[var(--app-bg)] text-[var(--app-text-primary)]">
      <header className="fixed top-0 z-50 w-full border-b border-[var(--app-border-color)] bg-[var(--app-elevated-bg)]/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 sm:px-6">
          <button
            type="button"
            className="flex items-center gap-2 text-left text-lg font-semibold"
            onClick={() => navigate('/')}
          >
            <PenLine size={20} />
            觉知日记
          </button>
          {isAuthenticated ? (
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
              <Avatar icon={<User size={16} />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          ) : (
            <Button icon={<LogIn size={16} />} onClick={() => navigate('/login')}>
              登录
            </Button>
          )}
        </div>
      </header>

      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-4 pb-16 pt-28 sm:px-6">
        <div className="max-w-2xl">
          <Typography.Title level={1} style={{ marginBottom: 20, fontSize: 48, lineHeight: 1.12 }}>
            私密觉察日记
          </Typography.Title>
          <Typography.Paragraph className="text-lg leading-8 text-[var(--app-text-secondary)]">
            这不是打卡，不是治疗，不是变好计划。只是一个每天陪你看一眼自己心上褶皱的地方。
          </Typography.Paragraph>
          <Typography.Paragraph className="text-lg leading-8 text-[var(--app-text-secondary)]">
            你可以不写，可以乱写，可以写同一个念头一百天。没有进度条，没有勋章。
          </Typography.Paragraph>
          <Flex gap={12} wrap="wrap" className="mt-8">
            <Button
              type="primary"
              size="large"
              icon={<PenLine size={18} />}
              onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
            >
              开始书写
            </Button>
            <Button size="large" onClick={() => navigate(isAuthenticated ? '/journal/recent' : '/login')}>
              {isAuthenticated ? '最近回看' : '登录'}
            </Button>
          </Flex>
        </div>
        <div className="mt-16 border-l-2 border-[var(--app-border-color)] pl-5 text-[var(--app-text-secondary)]">
          <p className="mb-2">今日一问</p>
          <p className="text-xl leading-9 text-[var(--app-text-primary)]">
            如果不用急着变好，今天你最想诚实写下什么？
          </p>
        </div>
      </section>
    </main>
  )
}
