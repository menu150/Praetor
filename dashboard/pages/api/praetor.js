import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end('Method Not Allowed');

  const { message } = req.body;
  if (!message) return res.status(400).json({ error: 'Missing message' });

  let port = '5000'; // fallback
  try {
    const portPath = path.join(process.cwd(), '..', '.flask_port');
    port = fs.readFileSync(portPath, 'utf-8').trim();
  } catch (e) {
    console.warn("[⚠️] Could not read .flask_port, falling back to 5000");
  }

  try {
    const response = await fetch(`http://localhost:${port}/api/praetor/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey YOUR_FLASK_KEY_HERE',
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    console.error('[❌] Proxy error:', err);
    res.status(500).json({ error: 'Proxy request failed' });
  }
}
