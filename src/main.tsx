import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { Signup } from './features/Signup/Signup.tsx';
import { Login } from './features/Login/Login.tsx';
// import SignUpPages from './features/Signup/Signup.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Login />
  </StrictMode>,
)
