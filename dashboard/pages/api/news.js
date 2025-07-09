export default async function handler(req, res) {
  const apiKey = process.env.NEWSAPI_KEY;
  const url = `https://newsapi.org/v2/top-headlines?country=us`;

  try {
    const response = await fetch(url, {
      headers: { 'X-Api-Key': apiKey }
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    console.error('News fetch error:', err);
    res.status(500).json({ status: 'error', message: err.message });
  }
}
