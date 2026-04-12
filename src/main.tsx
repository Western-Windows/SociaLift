import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx';
import { Dashboard } from './features/Dashboard/Dashboard.tsx';
import { DashboardLayout } from './layouts/DashboardLayout/DashboardLayout.tsx';
import { Signup } from './features/Signup/Signup.tsx';
import {Login} from './features/Login/Login.tsx';
import '../tailwind.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
