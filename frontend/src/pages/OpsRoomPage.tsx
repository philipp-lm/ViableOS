import { useOpsStore } from '../store/useOpsStore';
import { ConnectionPanel } from '../components/ops/ConnectionPanel';
import { AgentStatusGrid } from '../components/ops/AgentStatusGrid';
import { ActivityFeed } from '../components/ops/ActivityFeed';
import { SignalInbox } from '../components/ops/SignalInbox';
import { WorkPackageBoard } from '../components/ops/WorkPackageBoard';
import { PendingDecisions } from '../components/ops/PendingDecisions';

export function OpsRoomPage() {
  const connected = useOpsStore((s) => s.connected);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold">Operations Room</h1>
      <ConnectionPanel />

      {connected && (
        <>
          <AgentStatusGrid />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ActivityFeed />
            <SignalInbox />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <WorkPackageBoard />
            <PendingDecisions />
          </div>
        </>
      )}

      {!connected && (
        <div className="flex flex-col items-center justify-center h-[40vh] gap-4">
          <div className="text-4xl">📡</div>
          <p className="text-sm text-[var(--color-muted)] max-w-md text-center">
            Connect to a running OpenClaw or LangGraph deployment to monitor your agent system in real-time.
          </p>
        </div>
      )}
    </div>
  );
}
