import { NextRequest, NextResponse } from 'next/server';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function forward(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const route = path.join('/');
  const permitted = request.method === 'GET'
    ? /^(status|locations|charts\/[0-9a-f-]{36}(\/(analysis|image\.svg|access))?)$/.test(route)
    : /^(chart|analyze|access\/report|charts\/[0-9a-f-]{36}\/(ask|revalidate|access))$/.test(route);
  if (!permitted) return NextResponse.json({detail:'接口不存在'},{status:404});
  let body: string | undefined;
  if (request.method === 'POST') {
    const origin = request.headers.get('origin');
    // Browsers must be same-origin. Local CLI requests without Origin are allowed behind the private service boundary.
    if (origin && new URL(origin).host !== request.headers.get('host'))
      return NextResponse.json({detail:'跨站请求已拒绝'},{status:403});
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = []; let size = 0;
    if (reader) while (true) { const part = await reader.read(); if(part.done) break; size += part.value.length;
      if(size > 65536) { await reader.cancel(); return NextResponse.json({detail:'请求内容过大'},{status:413}); } chunks.push(part.value); }
    body = Buffer.concat(chunks).toString('utf8');
  }
  try {
    // Forward only this application's session, never parent-domain NØTA cookies.
    const session = request.cookies.get('ziping_master_session')?.value;
    const headers: Record<string,string> = {'Content-Type':'application/json'};
    if(session && /^[A-Za-z0-9_-]{30,100}$/.test(session)) headers.Cookie = `ziping_master_session=${session}`;
    const upstream = await fetch(`${process.env.API_BASE_URL || 'http://127.0.0.1:8000'}/api/v1/${route}`, {
      method:request.method,headers,body,cache:'no-store',signal:AbortSignal.timeout(route.endsWith('/ask')?95000:45000) });
    const response = new NextResponse(upstream.body,{status:upstream.status,headers:{'Content-Type':upstream.headers.get('content-type') || 'application/json; charset=utf-8','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff',...(route.endsWith('image.svg') ? {'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'"} : {})}});
    for(const cookie of upstream.headers.getSetCookie()) if(cookie.startsWith('ziping_master_session=')) response.headers.append('Set-Cookie',cookie);
    return response;
  } catch {
    return NextResponse.json({detail:route.endsWith('/ask')?'这次解读未能完成，请稍后重试。':'报告服务暂不可用，请稍后重试。'},{status:502});
  }
}
export const GET = forward;
export const POST = forward;
