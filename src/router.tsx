import { createBrowserRouter } from 'react-router-dom'
import { LandingPage } from './features/LandingPage/sections/LandingPage.tsx'
import { HomePage } from './features/HomePage/sections/HomePage.tsx'
import { Dashboard } from './features/Dashboard/Dashboard.tsx'
import { PostGeneration } from './features/PostGeneration/index.ts'
import { DashboardLayout } from './layouts/DashboardLayout/DashboardLayout.tsx'
import { GettingStarted } from './features/GettingStarted/GettingStarted.tsx'
import { Login } from './features/Login/Login.tsx'
import { Signup } from './features/Signup/Signup.tsx'

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/landing', element: <LandingPage /> },
  { path: '/home', element: <DashboardLayout><HomePage /> </DashboardLayout> },
  { path: '/getting-started', element: <GettingStarted /> },
  { path: '/dashboard', element: <DashboardLayout><Dashboard /> </DashboardLayout> },
  { path: '/post-gen', element: <DashboardLayout><PostGeneration /></DashboardLayout> },
  { path: '/signin', element: <Login /> },
  { path: '/login', element: <Login /> },
  { path: '/signup', element: <Signup /> },
  { path: '*', element: <LandingPage /> }
])
