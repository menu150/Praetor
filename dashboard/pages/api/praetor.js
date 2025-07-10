export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end('Method Not Allowed')

  const { message } = req.body
  if (!message) return res.status(400).json({ error: 'Missing message' })

  try {
    const response = await fetch('http://localhost:5050/api/praetor/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey 3R8UPlfH4UgTPP6RuCdMzkEUuz8rxv3wzrb7YaGfnPQ',
      },
      body: JSON.stringify({ message }),
    })

    const data = await response.json()
    res.status(200).json(data)
  } catch (err) {
    console.error('[❌] Proxy error:', err)
    res.status(500).json({ error: 'Proxy request failed' })
  }
}
