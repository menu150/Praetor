'use client';
import { useState } from 'react';

export default function ChatWidget() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { sender: 'You', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'Praetor', text: data.reply }]);
    } catch {
      setMessages(prev => [...prev, { sender: 'Praetor', text: '⚠ Chat unavailable.' }]);
    }
  }

  return (
    <div className="fixed bottom-0 left-64 right-0 bg-white border-t p-3">
      <div className="max-h-40 overflow-y-auto text-sm mb-2">
        {messages.map((m, i) => (
          <div key={i}><strong>{m.sender}:</strong> {m.text}</div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          className="flex-1 border px-2 py-1 rounded"
          placeholder="Ask Praetor..."
        />
        <button onClick={sendMessage} className="px-3 py-1 bg-blue-600 text-white rounded">Send</button>
      </div>
    </div>
  );
}
