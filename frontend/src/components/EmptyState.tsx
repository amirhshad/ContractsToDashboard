import { Link } from 'react-router-dom'
import { Upload, FileText, Sparkles, ArrowRight, CheckCircle } from 'lucide-react'

interface EmptyStateProps {
  type: 'dashboard' | 'contracts' | 'recommendations' | 'timeline'
}

export default function EmptyState({ type }: EmptyStateProps) {
  const configs = {
    dashboard: {
      icon: FileText,
      title: 'Welcome to Clausemate!',
      description: 'Start by uploading your first contract to get AI-powered insights.',
      cta: 'Upload Your First Contract',
      link: '/upload',
      tips: [
        'Upload PDF contracts (up to 5 documents at once)',
        'AI will extract costs, dates, and key terms',
        'Get personalized recommendations to save money',
      ],
    },
    contracts: {
      icon: FileText,
      title: 'No contracts yet',
      description: 'Upload your first contract to start tracking.',
      cta: 'Upload Contract',
      link: '/upload',
      tips: [
        'Click "Upload Contract" to get started',
        'Supported formats: PDF only',
        'You can upload multiple related documents',
      ],
    },
    recommendations: {
      icon: Sparkles,
      title: 'No recommendations yet',
      description: 'Upload contracts first to get AI-powered recommendations.',
      cta: 'Upload Contracts',
      link: '/upload',
      tips: [
        'AI analyzes your contracts for savings opportunities',
        'Get alerts for risky contract terms',
        'Never miss a renewal deadline',
      ],
    },
    timeline: {
      icon: FileText,
      title: 'No timeline to show',
      description: 'Add contracts with start and end dates to see your timeline.',
      cta: 'Upload Contracts',
      link: '/upload',
      tips: [
        'Timeline shows contract dates and renewal deadlines',
        'Helps you track upcoming expirations',
        'Cancellation deadlines are also displayed',
      ],
    },
  }

  const config = configs[type]
  const Icon = config.icon

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div className="text-center max-w-md mx-auto">
        <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="w-8 h-8 text-primary-600" />
        </div>
        
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          {config.title}
        </h3>
        
        <p className="text-gray-600 mb-6">
          {config.description}
        </p>

        <Link
          to={config.link}
          className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 transition-colors w-full sm:w-auto"
        >
          <Upload className="w-5 h-5 mr-2" />
          {config.cta}
          <ArrowRight className="w-5 h-5 ml-2" />
        </Link>

        <div className="mt-8 pt-6 border-t border-gray-100">
          <p className="text-sm font-medium text-gray-700 mb-3">Getting started tips:</p>
          <ul className="text-sm text-gray-500 space-y-2">
            {config.tips.map((tip, i) => (
              <li key={i} className="flex items-start">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
