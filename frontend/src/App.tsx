import { Sidebar } from './components/Sidebar';
import { WizardPage } from './pages/WizardPage';
import { DashboardPage } from './pages/DashboardPage';
import { useConfigStore } from './store/useConfigStore';

export default function App() {
  const view = useConfigStore((s) => s.view);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto">
        {view === 'wizard' ? <WizardPage /> : <DashboardPage />}
      </main>
    </div>
  );
}
