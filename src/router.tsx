// import {createBrowserRouter} from 'react-router-dom'


// ROUTING EXAMPLE (commented out for now, but can be used as a template for future routes)
// import {createBrowserRouter} from 'react-router-dom'

// import { ProtectedRoute } from './components/ProtectedRoute';
// import { MainLayout } from './layouts/MainLayout';
// import { DashboardPage } from './pages/DashboardPage';

// export const router = createBrowserRouter([
//     {
//         // 1. The router hits the ProtectedRoute guard first
//         element: <ProtectedRoute />,
//         children: [
//             {
//                 // 2. If the user passes the guard, render the Layout
//                 element: <MainLayout />,
//                 children: [
//                     // 3. The specific page is injected into the layout
//                     { path: '/dashboard', element: <DashboardPage /> }
//                 ]
//             }
//         ]
//     }
// ]);