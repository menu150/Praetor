'use client';
import { useState, useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default function DashboardPage() {
  const [articles, setArticles] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const chartRef = useRef(null);

  // Initialize Chart.js and metrics
  useEffect(() => {
    const ctx = chartRef.current.getContext('2d');
    const rpmData = [80,95,110,130,150,140,160,170,180,155];
    const labels  = ['9:50','9:55','10:00','10:05','10:10','10:15','10:20','10:25','10:30','Now'];
    new Chart(ctx, {
      type: 'line',
      data: { labels, datasets: [{ label: 'Req/min', data: rpmData, fill: false, tension: 0.4 }] },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  }, []);

  // Fetch news via internal proxy
  useEffect(() => {
    async function loadNews() {
      try {
        const res = await fetch('/api/news');
        const json = await res.json();
        setArticles(json.articles || []);
      } catch (err) {
        console.error('News fetch error:', err);
      }
    }
    loadNews();
  }, []);

  // Send chat messages
  const handleSend = async () => {
    if (!chatInput.trim()) return;
    setChatMessages(msgs => [...msgs, { sender: 'You', text: chatInput }]);
    const message = chatInput;
    setChatInput('');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const { reply } = await res.json();
      setChatMessages(msgs => [...msgs, { sender: 'Praetor', text: reply }]);
    } catch {
      setChatMessages(msgs => [...msgs, { sender: 'Praetor', text: 'Error: chat service unreachable.' }]);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white border-r p-4">
        <h2 className="text-xl font-bold mb-6">Praetor Dashboard</h2>
        <nav>
          <ul>
            {['Overview','Console','Skills','Integrations','Settings'].map(item => (
              <li key={item} className="mb-2 hover:text-blue-600 cursor-pointer">{item}</li>
            ))}
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-semibold">Overview</h1>
          <button className="px-4 py-2 bg-white border rounded">Toggle Dark Mode</button>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500 text-sm">Requests / min</h2>
            <p className="text-2xl font-bold">155</p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500 text-sm">Agent uptime</h2>
            <p className="text-2xl font-bold">99.8%</p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500 text-sm">Error rate</h2>
            <p className="text-2xl font-bold">1.2%</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded shadow mb-6">
          <canvas ref={chartRef}></canvas>
        </div>
        <div className="bg-white p-4 rounded shadow mb-6">
          <h2 className="text-xl font-semibold mb-2">Latest News</h2>
          <div className="space-y-4">
            {articles.length > 0 ? articles.map((a,i) => (
              <div key={i} className="p-2 border-b">
                <a href={a.url} target="_blank" className="text-blue-600 font-medium">{a.title}</a>
                <p className="text-sm text-gray-500">{new Date(a.publishedAt).toLocaleString()}</p>
              </div>
            )) : <p className="text-gray-500">Loading news...</p>}
          </div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-2">Chat with Praetor</h2>
          <div className="h-48 overflow-y-auto border p-2 mb-2">
            {chatMessages.map((m,idx) => <div key={idx}><strong>{m.sender}:</strong> {m.text}</div>)}
          </div>
          <div className="flex">
            <input
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              className="flex-1 border rounded p-2 mr-2"
              placeholder="Type a message..."
            />
            <button onClick={handleSend} className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
          </div>
        </div>
      </main>
    </div>
  );
}
