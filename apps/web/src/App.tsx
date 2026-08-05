import { Routes, Route, Link } from 'react-router-dom'

function Home() {
  return (
    <div className="p-8 max-w-4xl mx-auto text-center space-y-6">
      <h1 className="text-4xl font-extrabold text-indigo-600 tracking-tight">
        Frontend (Vite + React + Tailwind v3 + React Router)
      </h1>
      <p className="text-slate-600 text-lg">
        Welcome to your Turborepo monorepo starter page!
      </p>
      <div className="flex justify-center gap-4">
        <Link
          to="/about"
          className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium shadow"
        >
          Go to About Page
        </Link>
      </div>
    </div>
  )
}

function About() {
  return (
    <div className="p-8 max-w-4xl mx-auto text-center space-y-6">
      <h1 className="text-3xl font-bold text-slate-800">About Page</h1>
      <p className="text-slate-600">
        React Router DOM is set up and handling client-side routing.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          to="/"
          className="px-5 py-2.5 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300 transition font-medium"
        >
          Back to Home
        </Link>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <nav className="border-b bg-white border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <span className="font-bold text-xl tracking-wide text-indigo-600">RAG Chatbot Monorepo</span>
        <div className="space-x-6 text-sm font-semibold">
          <Link to="/" className="text-slate-600 hover:text-indigo-600 transition">Home</Link>
          <Link to="/about" className="text-slate-600 hover:text-indigo-600 transition">About</Link>
        </div>
      </nav>
      <main className="pt-10">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </div>
  )
}
