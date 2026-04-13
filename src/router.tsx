import { createBrowserRouter } from 'react-router-dom'
import { LandingPage } from './features/LandingPage/sections/LandingPage.tsx'
import { HomePage } from './features/HomePage/sections/HomePage.tsx'
import { GettingStarted_1_0 } from './features/GettingStarted_1_0/GettingStarted_1_0.tsx'
import { GettingStarted_1_1 } from './features/GettingStarted_1_1/GettingStarted_1_1.tsx'
import { GettingStarted_1_2 } from './features/GettingStarted_1_2/GettingStarted_1_2.tsx'
import { GettingStarted_2_0 } from './features/GettingStarted_2_0/GettingStarted_2_0.tsx'
import { GettingStarted_3_0 } from './features/GettingStarted_3_0/GettingStarted_3_0.tsx'
import { GettingStarted_3_1 } from './features/GettingStarted_3_1/GettingStarted_3_1.tsx'
import { GettingStarted_3_2 } from './features/GettingStarted_3_2/GettingStarted_3_2.tsx'
import { GettingStarted_3_3 } from './features/GettingStarted_3_3/GettingStarted_3_3.tsx'
import { Dashboard } from './features/Dashboard/Dashboard.tsx'
import { PostGeneration_1_0 } from './features/PostGeneration_1_0/index.ts'
import { PostGeneration_1_1A } from './features/PostGeneration_1_1A/index.ts'
import { PostGeneration_1_1B } from './features/PostGeneration_1_1B/index.ts'
import { PostGeneration_1_2 } from './features/PostGeneration_1_2/index.ts'
import { DashboardLayout } from './layouts/DashboardLayout/DashboardLayout.tsx'
import { Login } from './features/Login/Login.tsx'
import { Signup } from './features/Signup/Signup.tsx'

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/landing', element: <LandingPage /> },
  { path: '/home', element: <DashboardLayout><HomePage /> </DashboardLayout> },
  { path: '/getting-started/1-0', element: <GettingStarted_1_0 /> },
  { path: '/getting-started/1-1', element: <GettingStarted_1_1 /> },
  { path: '/getting-started/1-2', element: <GettingStarted_1_2 /> },
  { path: '/getting-started/2-0', element: <GettingStarted_2_0 /> },
  { path: '/getting-started/3-0', element: <GettingStarted_3_0 /> },
  { path: '/getting-started/3-1', element: <GettingStarted_3_1 /> },
  { path: '/getting-started/3-2', element: <GettingStarted_3_2 /> },
  { path: '/getting-started/3-3', element: <GettingStarted_3_3 /> },
  { path: '/dashboard', element: <DashboardLayout><Dashboard /> </DashboardLayout> },
  { path: '/post-gen1-0', element: <DashboardLayout><PostGeneration_1_0 /></DashboardLayout> },
  { path: '/post-gen1-1a', element: <DashboardLayout><PostGeneration_1_1A /></DashboardLayout> },
  { path: '/post-gen1-1b', element: <DashboardLayout><PostGeneration_1_1B /></DashboardLayout> },
  { path: '/post-gen1-2', element: <DashboardLayout><PostGeneration_1_2 /></DashboardLayout> },
  { path: '/signin', element: <Login /> },
  { path: '/login', element: <Login /> },
  { path: '/signup', element: <Signup /> },
  { path: '*', element: <LandingPage /> }
])
