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
          colorPrimary: isDark ? '#c8d7bc' : '#66715c',
          colorInfo: isDark ? '#b8d1ca' : '#6f8f8a',
          colorSuccess: isDark ? '#a8c39b' : '#6f8f54',
          colorWarning: isDark ? '#d0b57d' : '#8b7355',
          colorError: isDark ? '#d79a91' : '#9b5a50',
          borderRadius: 8,
          colorBgBase: isDark ? '#2f3c38' : '#f6faf5',
          colorBgLayout: isDark ? '#2f3c38' : '#edf5ee',
          colorTextBase: isDark ? '#edf5ee' : '#26362f',
          colorBorder: isDark ? 'rgba(200, 215, 188, 0.22)' : 'rgba(111, 143, 138, 0.24)',
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
            headerBg: isDark ? '#34443f' : '#f6faf5',
            bodyBg: 'transparent',
          },
          Card: {
            borderRadiusLG: 8,
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
