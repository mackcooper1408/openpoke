export const runtime = 'nodejs';

export async function POST(req: Request) {
  const serverBase = process.env.PY_SERVER_URL || 'http://localhost:8001';
  const url = `${serverBase}/api/v1/sms/connect`;

  try {
    const body = await req.json();
    const formData = new URLSearchParams();
    formData.append('account_sid', body.account_sid || '');
    formData.append('auth_token', body.auth_token || '');
    formData.append('phone_number', body.phone_number || '');

    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

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
