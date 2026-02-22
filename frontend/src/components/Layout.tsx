import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Upload, FileText, LogOut, Search, Calendar, Sparkles, Settings } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { signOut, user } = useAuth()
  const location = useLocation()

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', mobileLabel: 'Home' },
    { path: '/upload', icon: Upload, label: 'Upload', mobileLabel: 'Upload' },
    { path: '/contracts', icon: FileText, label: 'Contracts', mobileLabel: 'Contracts' },
    { path: '/timeline', icon: Calendar, label: 'Timeline', mobileLabel: 'Timeline' },
    { path: '/analysis', icon: Search, label: 'Analysis', mobileLabel: 'Analysis' },
    { path: '/recommendations', icon: Sparkles, label: 'AI Insights', mobileLabel: 'Insights' },
    { path: '/settings', icon: Settings, label: 'Settings', mobileLabel: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-primary-600">
                Clausemate
              </h1>
              <nav className="hidden md:flex space-x-4">
                {navItems.map(({ path, icon: Icon, label }) => (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname === path || (path === '/analysis' && location.pathname.includes('/analysis'))
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{label}</span>
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={signOut}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile nav */}
      <nav className="md:hidden bg-white border-b border-gray-200 overflow-x-auto">
        <div className="flex justify-between min-w-max px-2 py-2">
          {navItems.map(({ path, icon: Icon, mobileLabel }) => (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center px-2 py-1 text-[10px] min-w-[52px] ${
                location.pathname === path || (path === '/analysis' && location.pathname.includes('/analysis'))
                  ? 'text-primary-600'
                  : 'text-gray-600'
              }`}
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="truncate">{mobileLabel}</span>
            </Link>
          ))}
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
