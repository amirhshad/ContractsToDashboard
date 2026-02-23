import { Link } from 'react-router-dom'
import { FileText, Sparkles, Calendar, Search, TrendingDown, ArrowRight, CheckCircle, Zap, Shield, Clock } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Clausemate</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Sign in
              </Link>
              <Link
                to="/login"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            AI Contract Intelligence for{' '}
            <span className="text-primary-600">Growing Businesses</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Stop managing contracts in spreadsheets. Upload your contracts and let AI extract key dates, costs, and terms instantly.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/login"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-primary-700 transition-colors inline-flex items-center justify-center gap-2"
            >
              Start Free <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#features"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-gray-50 transition-colors inline-flex items-center justify-center"
            >
              See How It Works
            </a>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            No credit card required • Free plan available
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything you need to manage contracts
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Powerful features designed for small teams who need enterprise-level contract management without the complexity.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Extraction</h3>
              <p className="text-gray-600">
                Upload any contract PDF and our AI extracts provider, dates, costs, and key terms automatically.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Calendar className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Renewal Tracking</h3>
              <p className="text-gray-600">
                Never miss a renewal. Get alerts before auto-renewals kick in and cost you money.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingDown className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Cost Optimization</h3>
              <p className="text-gray-600">
                AI analyzes your contracts and recommends ways to reduce spending and consolidate vendors.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Search className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Instant Search</h3>
              <p className="text-gray-600">
                Search across all your contracts instantly. Find any term, clause, or provider in seconds.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Insights</h3>
              <p className="text-gray-600">
                Get AI-generated insights about risks, opportunities, and negotiation points.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">5-Minute Setup</h3>
              <p className="text-gray-600">
                No implementation team needed. Upload your first contract and get insights in minutes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-gray-600">
              Start free, upgrade when you're ready
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free */}
            <div className="border border-gray-200 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Free</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">$0</p>
              <p className="text-gray-600 mb-6">Perfect for getting started</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> 3 contracts
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Basic AI analysis
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Dashboard view
                </li>
              </ul>
              <Link
                to="/login"
                className="block w-full border border-gray-300 text-gray-700 py-3 rounded-lg font-medium text-center hover:bg-gray-50 transition-colors"
              >
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="border-2 border-primary-600 rounded-2xl p-8 relative">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                Most Popular
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Pro</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">$29</p>
              <p className="text-gray-600 mb-6">per month</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Unlimited contracts
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Full AI insights
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Timeline view
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Export to CSV
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Priority support
                </li>
              </ul>
              <Link
                to="/login"
                className="block w-full bg-primary-600 text-white py-3 rounded-lg font-medium text-center hover:bg-primary-700 transition-colors"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Team */}
            <div className="border border-gray-200 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Team</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">$79</p>
              <p className="text-gray-600 mb-6">per month</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Everything in Pro
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Up to 5 team members
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Shared contracts
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <CheckCircle className="w-5 h-5 text-green-500" /> Team analytics
                </li>
              </ul>
              <Link
                to="/login"
                className="block w-full border border-gray-300 text-gray-700 py-3 rounded-lg font-medium text-center hover:bg-gray-50 transition-colors"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to take control of your contracts?
          </h2>
          <p className="text-primary-100 text-lg mb-8">
            Join thousands of businesses saving time and money with Clausemate.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
          >
            Get Started Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-primary-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">C</span>
              </div>
              <span className="font-medium text-gray-900">Clausemate</span>
            </div>
            <p className="text-gray-500 text-sm">
              © 2026 Clausemate. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
