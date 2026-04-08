import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GettingStarted_1_0 } from './features/GettingStarted_1_0/GettingStarted_1_0.tsx'
import { GettingStarted_1_1 } from './features/GettingStarted_1_1/GettingStarted_1_1.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GettingStarted_1_1 />
  </StrictMode>,
)
