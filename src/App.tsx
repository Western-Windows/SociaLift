import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { LandingPage } from "./features/LandingPage/sections/LandingPage.tsx"
import { HomePage } from "./features/HomePage/sections/HomePage.tsx"
import { GettingStarted_1_0 } from "./features/GettingStarted_1_0/GettingStarted_1_0.tsx"
import "./App.css"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/getting-started" element={<GettingStarted_1_0 />} />
        <Route
          path="/signin"
          element={
            <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-900 px-4">
              <div className="rounded-3xl bg-white p-10 shadow-xl max-w-md w-full text-center">
                <h1 className="text-3xl font-semibold mb-4">Sign In</h1>
                <p className="text-sm text-slate-600 mb-6">
                  This page is ready for your sign in form.
                </p>
                <a
                  className="inline-flex items-center justify-center rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-500"
                  href="/"
                >
                  Back to landing
                </a>
              </div>
            </div>
          }
        />
        <Route
          path="/signup"
          element={
            <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-900 px-4">
              <div className="rounded-3xl bg-white p-10 shadow-xl max-w-md w-full text-center">
                <h1 className="text-3xl font-semibold mb-4">Sign Up</h1>
                <p className="text-sm text-slate-600 mb-6">
                  This page is ready for your sign up form.
                </p>
                <a
                  className="inline-flex items-center justify-center rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-500"
                  href="/"
                >
                  Back to landing
                </a>
              </div>
            </div>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;
