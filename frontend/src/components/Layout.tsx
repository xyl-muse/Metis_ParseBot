import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  BookOpen,
  Settings,
  Zap,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '仪表盘' },
  { to: '/contents', icon: FileText, label: '内容库' },
  { to: '/learning', icon: BookOpen, label: '学习中心' },
  { to: '/settings', icon: Settings, label: '设置' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* 移动端侧边栏遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={clsx(
          'fixed top-0 left-0 z-50 h-full w-64 transform transition-transform duration-300 lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col glass">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200/50 dark:border-slate-700/50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl gradient-bg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold gradient-text">Metis</h1>
                <p className="text-xs text-slate-500">智能学习助手</p>
              </div>
            </div>
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* 导航菜单 */}
          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                    isActive
                      ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  )
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* 底部信息 */}
          <div className="p-4 border-t border-slate-200/50 dark:border-slate-700/50">
            <div className="px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                muse&iflow
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                v0.1.0
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <div className="lg:pl-64">
        {/* 顶部栏 */}
        <header className="sticky top-0 z-30 glass border-b border-slate-200/50 dark:border-slate-700/50">
          <div className="flex items-center justify-between px-4 py-3 lg:px-6">
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex-1 lg:flex-none">
              <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">
                {navItems.find((item) => item.to === location.pathname)?.label || '仪表盘'}
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <StatusIndicator />
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function StatusIndicator() {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-100 dark:bg-green-900/30">
      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
      <span className="text-xs font-medium text-green-700 dark:text-green-400">运行中</span>
    </div>
  )
}
