import { Link } from 'react-router-dom'
import { FileText, Sparkles, Calendar, Search, TrendingDown, ArrowRight, CheckCircle, ChevronRight, Bell } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">C</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">Clausemate</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-gray-400 hover:text-white font-medium transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/login"
                className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-5 py-2.5 rounded-xl font-semibold hover:opacity-90 transition-opacity"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 py-32 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-sm text-gray-300">Now with AI-powered insights</span>
          </div>
          
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent">
              Smart Contract
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Management
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Upload your contracts and let AI extract key dates, costs, and terms. 
            Get smart recommendations to optimize your spending.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/login"
              className="group bg-gradient-to-r from-purple-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="#features"
              className="border border-white/20 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-white/5 transition-all flex items-center justify-center gap-2"
            >
              See Features
              <ChevronRight className="w-5 h-5" />
            </a>
          </div>
          
          <p className="mt-6 text-sm text-gray-500">
            No credit card required • 14-day free trial
          </p>
        </div>

        {/* Dashboard Preview */}
        <div className="max-w-5xl mx-auto mt-20">
          <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-1">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-blue-500/10"></div>
            <div className="relative rounded-xl bg-[#0f0f14] p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                  <p className="text-gray-500 text-sm mb-1">Total Contracts</p>
                  <p className="text-2xl font-bold text-white">24</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                  <p className="text-gray-500 text-sm mb-1">Monthly Spend</p>
                  <p className="text-2xl font-bold text-purple-400">$2,847</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                  <p className="text-gray-500 text-sm mb-1">Savings</p>
                  <p className="text-2xl font-bold text-green-400">$420</p>
                </div>
              </div>
              <div className="h-32 bg-white/5 rounded-xl border border-white/5 flex items-center justify-center">
                <span className="text-gray-500">📊 Spending Chart Preview</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Everything you need
              </span>
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Powerful features designed for modern teams
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: FileText, title: 'AI Extraction', desc: 'Upload any PDF and get instant extraction of dates, costs, and terms', color: 'from-purple-500 to-pink-500' },
              { icon: Calendar, title: 'Renewal Tracking', desc: 'Never miss a renewal with smart alerts before auto-renewals kick in', color: 'from-blue-500 to-cyan-500' },
              { icon: TrendingDown, title: 'Cost Optimization', desc: 'AI recommendations to reduce spending and consolidate vendors', color: 'from-green-500 to-emerald-500' },
              { icon: Search, title: 'Instant Search', desc: 'Find any contract, term, or clause in seconds across all your documents', color: 'from-orange-500 to-red-500' },
              { icon: Sparkles, title: 'Smart Insights', desc: 'AI-generated insights about risks, opportunities, and negotiation points', color: 'from-yellow-500 to-orange-500' },
              { icon: Bell, title: 'Smart Reminders', desc: 'Get email alerts for upcoming renewals and important deadlines', color: 'from-cyan-500 to-blue-500' },
            ].map((feature, i) => (
              <div key={i} className="group bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:border-white/20 transition-all">
                <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 py-24 px-4 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                How it works
              </span>
            </h2>
            <p className="text-lg text-gray-400">Get started in three simple steps</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Upload Contracts', desc: 'Drag and drop your contract PDFs or upload from your computer' },
              { step: '02', title: 'AI Analysis', desc: 'Our AI extracts key information: dates, costs, terms, and risks' },
              { step: '03', title: 'Get Insights', desc: 'Receive smart recommendations to optimize your contracts' },
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="text-6xl font-bold text-white/5 mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative z-10 py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Simple pricing
              </span>
            </h2>
            <p className="text-lg text-gray-400">Start free, upgrade when you're ready</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {/* Free */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-white mb-2">Free</h3>
              <p className="text-4xl font-bold text-white mb-2">$0</p>
              <p className="text-gray-500 mb-6">Forever free</p>
              <ul className="space-y-3 mb-8">
                {['3 contracts', 'Basic AI analysis', 'Dashboard view', 'Email support'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-gray-400">
                    <CheckCircle className="w-5 h-5 text-purple-400" /> {item}
                  </li>
                ))}
              </ul>
              <Link
                to="/login"
                className="block w-full border border-white/20 text-white py-3 rounded-xl font-medium text-center hover:bg-white/5 transition-colors"
              >
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="bg-gradient-to-b from-purple-500/20 to-blue-500/20 border border-purple-500/30 rounded-2xl p-8 relative">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-purple-500 to-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                Most Popular
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Pro</h3>
              <p className="text-4xl font-bold text-white mb-2">$29</p>
              <p className="text-gray-500 mb-6">per month</p>
              <ul className="space-y-3 mb-8">
                {['Unlimited contracts', 'Full AI insights', 'Timeline view', 'Export to CSV', 'Priority support'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-gray-300">
                    <CheckCircle className="w-5 h-5 text-blue-400" /> {item}
                  </li>
                ))}
              </ul>
              <Link
                to="/login"
                className="block w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 rounded-xl font-medium text-center hover:opacity-90 transition-opacity"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Team */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-white mb-2">Team</h3>
              <p className="text-4xl font-bold text-white mb-2">$79</p>
              <p className="text-gray-500 mb-6">per month</p>
              <ul className="space-y-3 mb-8">
                {['Everything in Pro', 'Up to 5 team members', 'Shared contracts', 'Team analytics', 'Dedicated support'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-gray-400">
                    <CheckCircle className="w-5 h-5 text-green-400" /> {item}
                  </li>
                ))}
              </ul>
              <Link
                to="/login"
                className="block w-full border border-white/20 text-white py-3 rounded-xl font-medium text-center hover:bg-white/5 transition-colors"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-3xl p-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Ready to take control?
            </h2>
            <p className="text-white/80 text-lg mb-8">
              Join thousands of businesses saving time and money with Clausemate.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 bg-white text-purple-600 px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-gray-100 transition-colors"
            >
              Get Started Free <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs">C</span>
              </div>
              <span className="font-medium text-gray-300">Clausemate</span>
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
