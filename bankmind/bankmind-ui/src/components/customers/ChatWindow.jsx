import { formatTime } from '../ui/shared';

const AGENT_COLORS = {
  acquisition: 'bg-accent-primary/20 text-accent-primary',
  onboarding:  'bg-accent-warning/20 text-accent-warning',
  adoption:    'bg-accent-success/20 text-accent-success',
  life_event:  'bg-accent-purple/20 text-accent-purple',
};

function ChatBubble({ message }) {
  const isAgent = message.sender === 'agent';
  const agentColor = AGENT_COLORS[message.agent_name] || 'bg-bm-border';

  return (
    <div className={`flex ${isAgent ? 'justify-end' : 'justify-start'} group`}>
      <div className="max-w-[80%]">
        <div className={`
          rounded-2xl px-4 py-2.5 text-sm leading-relaxed
          ${isAgent
            ? 'bg-accent-primary/20 text-text-primary rounded-br-sm'
            : 'bg-bg-elevated border border-bm-border text-text-secondary rounded-bl-sm'
          }
        `}>
          {message.content}
        </div>
        <div className={`flex items-center gap-2 mt-1 ${isAgent ? 'justify-end' : 'justify-start'}`}>
          {isAgent && message.agent_name && (
            <span className={`text-xs px-1.5 py-0.5 rounded ${agentColor}`}>
              {message.agent_name.replace('_', '-')}
            </span>
          )}
          {!isAgent && <span className="text-xs text-text-muted">Customer</span>}
          <span className="text-xs text-text-muted mono">{formatTime(message.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

export default function ChatWindow({ conversations, customerName, isLoading }) {
  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        {[1, 2, 3].map(i => (
          <div key={i} className={`flex ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
            <div className="h-12 w-48 bg-bg-elevated rounded-2xl animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  if (!conversations?.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-center">
        <div className="text-3xl mb-3">💬</div>
        <p className="text-sm text-text-muted">No conversations yet</p>
        <p className="text-xs text-text-muted mt-1">Conversations will appear here after agents run</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-bm-border bg-bg-surface/50">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-success animate-pulse" />
          <p className="text-sm font-medium text-text-primary">{customerName}</p>
          <span className="text-xs text-text-muted">· Simulated WhatsApp</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0A0E16]">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-[0.02] pointer-events-none"
          style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '20px 20px' }}
        />
        {conversations.map((msg) => (
          <ChatBubble key={msg.id} message={msg} />
        ))}
      </div>

      {/* Read-only indicator */}
      <div className="px-4 py-2.5 border-t border-bm-border bg-bg-surface/50">
        <p className="text-xs text-text-muted text-center">Read-only simulation view</p>
      </div>
    </div>
  );
}
