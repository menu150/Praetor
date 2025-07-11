import fetch from 'node-fetch';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Missing "message" in body' });
  }

  // Read port and API key from env (set these in .env.local)
  const FLASK_PORT = process.env.FLASK_PORT || '5000';
  const PRAETOR_KEY = process.env.PRAETOR_API_KEY;

  try {
    const flaskRes = await fetch(
      `http://localhost:${FLASK_PORT}/api/praetor/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `ApiKey ${PRAETOR_KEY}`,
        },
        body: JSON.stringify({ message }),
      }
    );

    // If Flask returns non-JSON (e.g. 404 HTML), fall back to text:
    const text = await flaskRes.text();
    try {
      // try parse JSON
      const data = JSON.parse(text);
      return res.status(flaskRes.status).json(data);
    } catch {
      // not JSON
      return res
        .status(502)
        .json({ error: 'Bad response from Praetor backend', body: text });
    }
  } catch (err) {
    console.error('[❌] Proxy to Flask failed:', err);
    return res.status(500).json({ error: 'Unable to reach Praetor backend' });
  }
}
