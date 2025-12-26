export const runtime = 'nodejs';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  if (!code) {
    return new Response(JSON.stringify({ ok: false, error: 'Missing authorization code' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  }

  if (!state) {
    return new Response(JSON.stringify({ ok: false, error: 'Missing state parameter' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  }

  const serverBase = process.env.PY_SERVER_URL || 'http://localhost:8001';
  const url = `${serverBase.replace(/\/$/, '')}/api/v1/whoop/callback?code=${encodeURIComponent(
    code
  )}&state=${encodeURIComponent(state)}`;

  try {
    const resp = await fetch(url);
    const data = await resp.json().catch(() => ({}));

    // Redirect to settings page with success/error message
    const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';
    const redirectUrl = data?.success
      ? `${frontendUrl}/?whoop_connected=true`
      : `${frontendUrl}/?whoop_error=${encodeURIComponent(data?.error || 'Connection failed')}`;

    return Response.redirect(redirectUrl, 302);
  } catch (e: any) {
    const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';
    return Response.redirect(
      `${frontendUrl}/?whoop_error=${encodeURIComponent(e?.message || 'Connection failed')}`,
      302
    );
  }
}
