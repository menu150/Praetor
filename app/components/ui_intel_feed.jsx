# ui_intel_feed.jsx (React component for Next.js)
import { useEffect, useState } from "react";

export default function IntelFeedPanel() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`/api/intel-feed${filter ? `?classification=${filter}` : ""}`);
      const data = await res.json();
      setItems(data.items);
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [filter]);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">🧠 Intel Feed</h2>
      <select
        className="border p-2 rounded"
        onChange={(e) => setFilter(e.target.value)}
        value={filter}
      >
        <option value="">All</option>
        <option value="geopolitical">Geopolitical</option>
        <option value="military">Military</option>
        <option value="domestic policy">Domestic Policy</option>
        <option value="foreign policy">Foreign Policy</option>
        <option value="economy">Economy</option>
        <option value="legal/judicial">Legal</option>
        <option value="cybersecurity">Cybersecurity</option>
        <option value="disinformation">Disinformation</option>
      </select>
      <div className="grid grid-cols-1 gap-4">
        {items.map((item, i) => (
          <div key={i} className="bg-white p-4 rounded-2xl shadow">
            <h3 className="font-bold text-lg">{item.title}</h3>
            <p className="text-sm text-gray-600">{new Date(item.published).toLocaleString()}</p>
            <p className="mt-2">{item.ai_summary}</p>
            <p className="text-xs mt-2 text-blue-500">Tags: {item.classification.join(", ")}</p>
            <a href={item.link} className="text-blue-600 underline text-sm" target="_blank">Source</a>
          </div>
        ))}
      </div>
    </div>
  );
}
