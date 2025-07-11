export default async function handler(req, res) {
  const { message } = req.body || {};
  if (!message) return res.status(400).json({ reply: 'Invalid message.' });

  // Replace this stub with actual LLM call
  return res.status(200).json({ reply: `Echo: ${message}` });
}
