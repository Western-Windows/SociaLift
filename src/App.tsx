import { Dashboard } from './features/Dashboard';
import { DashboardLayout } from './layouts/DashboardLayout/DashboardLayout';

function App() {
  return (
    <DashboardLayout>
      <Dashboard />
    </DashboardLayout>
  );
}

export default App;
