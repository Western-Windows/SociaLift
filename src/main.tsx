import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from "react-router-dom";

// 👇 THIS IS THE FIX: Pointing to the tailwind.css file in the root folder
import '../tailwind.css'; 

// Import your pages
import { LandingPage } from "./features/LandingPage/sections/LandingPage";
import { HomePage } from "./features/HomePage/sections/HomePage";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);