import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ site }) => {
  const origin = site?.toString().replace(/\/$/, '') || 'https://api-integration-hub.com';
  const body = [
    'User-agent: *',
    'Allow: /',
    '',
    `Sitemap: ${origin}/sitemap-index.xml`,
    '',
  ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
