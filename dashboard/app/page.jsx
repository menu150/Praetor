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
    const rpmData = [80, 95, 110, 130, 150, 140, 160, 170, 180, 155];
    const labels = ['9:50', '9:55', '10:00', '10:05', '10:10', '10:15', '10:20', '10:25', '10:30', '10:35'];
    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Requests per Minute',
          data: rpmData,
          fill: true,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
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

  // Send message to /api/chat
  async function handleSendChat() {
    if (!chatInput.trim()) return;
    setChatMessages(prev => [...prev, { from: 'You', text: chatInput }]);
    setChatInput('');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: chatInput })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { from: 'Praetor', text: data.reply }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { from: 'Praetor', text: 'Error: Chat service unreachable.' }]);
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-semibold">Overview</h1>
      </div>

      {/* Chart */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold mb-2">Request Rate</h2>
        <canvas ref={chartRef} />
      </div>

      {/* News Section */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold mb-2">Latest News</h2>
        {articles.length === 0 ? (
          <p>No news available.</p>
        ) : (
          <ul className="space-y-2">
            {articles.slice(0, 5).map((a, i) => (
              <li key={i} className="border-b pb-2">
                <a href={a.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{a.title}</a>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Chat Widget */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold mb-2">Praetor Chat</h2>
        <div className="h-48 overflow-y-auto border p-2 mb-2 bg-gray-50" id="chatWindow">
          {chatMessages.map((m, i) => (
            <div key={i}><strong>{m.from}:</strong> {m.text}</div>
          ))}
        </div>
        <div className="flex space-x-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            className="flex-1 border p-2 rounded"
            placeholder="Ask Praetor something..."
          />
          <button onClick={handleSendChat} className="bg-blue-600 text-white px-4 py-2 rounded">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
