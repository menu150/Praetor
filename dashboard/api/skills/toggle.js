import { get_connection } from '../../../memory_core';
export async function POST(req) {
  const { trigger, enabled } = await req.json();
  const conn = get_connection();
  conn.prepare(
    `UPDATE skills SET enabled = ? WHERE trigger = ?`
  ).run(enabled ? 1 : 0, trigger);

  return new Response(JSON.stringify({ trigger, enabled }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
