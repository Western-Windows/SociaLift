import { RouterProvider } from "react-router-dom"
import { router } from "./router.tsx"
import "./App.css"
import { useEffect } from "react";

function App() {
  useEffect(() => {
  fetch('http://127.0.0.1:8000/api/health')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("API connection failed:", error));
}, []);
  return <RouterProvider router={router} />
}

export default App;
