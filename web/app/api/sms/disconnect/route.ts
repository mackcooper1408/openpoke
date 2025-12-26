export const runtime = 'nodejs';

export async function POST() {
  const serverBase = process.env.PY_SERVER_URL || 'http://localhost:8001';
  const url = `${serverBase}/api/v1/sms/disconnect`;

  try {
    const resp = await fetch(url, { method: 'POST' });
    const data = await resp.json().catch(() => ({}));
    return new Response(JSON.stringify(data), {
      status: resp.status,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  } catch (e: any) {
    return new Response(
      JSON.stringify({ ok: false, error: 'Upstream error', detail: e?.message }),
      { status: 502, headers: { 'Content-Type': 'application/json; charset=utf-8' } }
    );
  }
}
