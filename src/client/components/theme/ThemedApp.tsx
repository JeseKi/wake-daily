import { App as AntdApp, ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from '../../App'
import { useThemeMode } from '../../hooks/useThemeMode'

export default function ThemedApp() {
  const { resolvedTheme } = useThemeMode()
  const isDark = resolvedTheme === 'dark'

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: isDark ? '#ffd2a8' : '#b15f3a',
          colorInfo: isDark ? '#ffd2a8' : '#b15f3a',
          colorSuccess: isDark ? '#8fb276' : '#6f8f54',
          colorWarning: isDark ? '#e0ad63' : '#b8792f',
          colorError: isDark ? '#e07a68' : '#b84a3c',
          borderRadius: 8,
          colorBgBase: isDark ? '#6d5749' : '#fffaf4',
          colorBgLayout: isDark ? '#6d5749' : '#fbf6ef',
          colorTextBase: isDark ? '#fff4e8' : '#2b211b',
          colorBorder: isDark ? 'rgba(255, 210, 168, 0.24)' : 'rgba(156, 119, 88, 0.26)',
          fontFamily:
            "'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', system-ui, -apple-system, sans-serif",
        },
        components: {
          Button: {
            controlHeight: 40,
            fontWeight: 600,
            paddingInline: 16,
          },
          Layout: {
            headerBg: isDark ? '#7c6555' : '#fffaf4',
            bodyBg: 'transparent',
          },
          Card: {
            borderRadiusLG: 12,
          },
        },
      }}
    >
      <AntdApp>
        <App />
      </AntdApp>
    </ConfigProvider>
  )
}
