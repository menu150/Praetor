import logger from '../../lib/logger';


export default async function handler(req, res) {
  try {
    const response = await fetch(...); // Your logic
    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    console.error('API error:', err);
    res.status(500).json({
      status: 'error',
      message: err.message || 'Unknown server error',
    });
  }
}
