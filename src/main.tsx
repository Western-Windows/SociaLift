import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GettingStarted_1_0 } from './features/GettingStarted_1_0/GettingStarted_1_0.tsx'
import { GettingStarted_1_1 } from './features/GettingStarted_1_1/GettingStarted_1_1.tsx'
import { GettingStarted_1_2 } from './features/GettingStarted_1_2/GettingStarted_1_2.tsx'
import { GettingStarted_2_0 } from './features/GettingStarted_2_0/GettingStarted_2_0.tsx'
import { GettingStarted_3_0 } from './features/GettingStarted_3_0/GettingStarted_3_0.tsx'
import { GettingStarted_3_1 } from './features/GettingStarted_3_1/GettingStarted_3_1.tsx'
import { GettingStarted_3_2 } from './features/GettingStarted_3_2/GettingStarted_3_2.tsx'
import { GettingStarted_3_3 } from './features/GettingStarted_3_3/GettingStarted_3_3.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GettingStarted_3_2 />
  </StrictMode>,
)
