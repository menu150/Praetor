import { get_connection, init_db } from '../../../memory_core';
export async function GET() {
  const conn = get_connection();
  const rows = conn.prepare(
    `SELECT trigger, action, path_or_command, enabled FROM skills`
  ).all();

  return new Response(JSON.stringify(rows), {
    headers: { 'Content-Type': 'application/json' }
  });
}
