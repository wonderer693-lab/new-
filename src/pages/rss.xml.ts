import type { APIRoute } from 'astro';
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ site }) => {
  const errors = await getCollection('errors');
  const integrations = await getCollection('integrations');
  const guides = await getCollection('guides');

  const allEntries = [
    ...errors.map(e => ({
      title: e.data.title,
      description: e.data.description,
      pubDate: new Date(e.data.lastUpdated),
      link: `/${e.data.tool}/errors/${e.data.errorCode}`,
    })),
    ...integrations.map(e => ({
      title: e.data.title,
      description: e.data.description,
      pubDate: new Date(e.data.lastUpdated),
      link: `/integrations/${e.data.integrationSlug}/errors/${e.data.errorSlug}`,
    })),
    ...guides.map(e => ({
      title: e.data.title,
      description: e.data.description,
      pubDate: new Date(e.data.lastUpdated),
      link: `/${e.data.tool}/migration/${e.id.replace(/^.*[\/\\]/, '').replace('.md', '')}`,
    })),
  ].sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime());

  return rss({
    title: 'API Integration Hub',
    description: 'Production-tested fixes for SaaS API integration errors.',
    site: site?.toString() || 'https://api-integration-hub.com',
    items: allEntries,
  });
};
