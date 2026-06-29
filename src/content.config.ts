import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const seoBase = {
  description: z.string().min(70, 'description must be 70+ chars for SEO snippets'),
  lastUpdated: z.string(),
  lastReviewed: z.string().optional(),
  keywords: z.array(z.string()).min(3, 'keywords are required for topical targeting'),
  ogImage: z.string().optional(),
  canonical: z.string().optional(),
  author: z.string().default('API Integration Hub'),
  noindex: z.boolean().default(false),
};

const errors = defineCollection({
  loader: glob({ pattern: '**/errors-*.md', base: './src/content' }),
  schema: z.object({
    title: z.string().min(40, 'title must be 40+ chars and include the error code + tool'),
    ...seoBase,
    tool: z.string(),
    errorCode: z.string(),
    errorName: z.string(),
    httpStatus: z.number(),
    category: z.string(),
    severity: z.enum(['low', 'medium', 'high', 'critical']),
    priority: z.number(),
    deadline: z.string().optional(),
    pageType: z.string().default('error-code'),
  }),
});

const integrations = defineCollection({
  loader: glob({ pattern: '**/int-*.md', base: './src/content' }),
  schema: z.object({
    title: z.string().min(40, 'title must name both tools + the failure'),
    ...seoBase,
    toolA: z.string(),
    toolB: z.string(),
    integrationSlug: z.string(),
    errorSlug: z.string(),
    errorName: z.string(),
    category: z.string(),
    errorType: z.enum(['error', 'silent-failure', 'partial-failure', 'performance']),
    severity: z.enum(['low', 'medium', 'high', 'critical']),
    priority: z.number(),
    pageType: z.string().default('integration-error'),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/migration-*.md', base: './src/content' }),
  schema: z.object({
    title: z.string().min(40, 'title must include the tool + migration goal'),
    ...seoBase,
    tool: z.string(),
    pageType: z.string().default('migration-guide'),
    priority: z.number(),
    deadline: z.string().optional(),
    errorCode: z.string().optional(),
    category: z.string().optional(),
    severity: z.string().optional(),
  }),
});

export const collections = { errors, integrations, guides };