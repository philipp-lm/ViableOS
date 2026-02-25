import { ProviderSelector } from '../components/chat/ProviderSelector';
import { ChatWindow } from '../components/chat/ChatWindow';
import { AssessmentPreview } from '../components/chat/AssessmentPreview';

export function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-4xl mx-auto">
      <ProviderSelector />
      <ChatWindow />
      <AssessmentPreview />
    </div>
  );
}
