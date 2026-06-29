import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data', 'processed');
const CONTENT_DIR = path.join(__dirname, '..', 'src', 'content');

const TOOL_TO_SLUG = {
  'hubspot': 'hubspot',
  'salesforce': 'salesforce',
  'activecampaign': 'activecampaign',
  'pipedrive': 'pipedrive',
  'mailchimp': 'mailchimp',
  'slack': 'slack',
  'zoho': 'zoho',
  'calendly': 'calendly',
  'make': 'make',
  'zapier': 'zapier',
};

const TOOL_DISPLAY = {
  'hubspot': 'HubSpot',
  'salesforce': 'Salesforce',
  'activecampaign': 'ActiveCampaign',
  'pipedrive': 'Pipedrive',
  'mailchimp': 'Mailchimp',
  'slack': 'Slack',
  'zoho': 'Zoho',
  'calendly': 'Calendly',
  'make': 'Make',
  'zapier': 'Zapier',
};

const SEVERITY_MAP = {
  '401': 'high',
  '402': 'medium',
  '403': 'high',
  '404': 'medium',
  '409': 'medium',
  '410': 'medium',
  '413': 'low',
  '414': 'low',
  '415': 'low',
  '420': 'medium',
  '422': 'medium',
  '423': 'low',
  '428': 'low',
  '429': 'high',
  '500': 'critical',
  '503': 'critical',
  '5XX': 'critical',
};

const CATEGORY_MAP = {
  '400': 'validation',
  '401': 'authentication',
  '402': 'billing',
  '403': 'permission',
  '404': 'not-found',
  '409': 'conflict',
  '410': 'deprecation',
  '413': 'payload',
  '414': 'payload',
  '415': 'configuration',
  '420': 'infrastructure',
  '422': 'validation',
  '423': 'rate-limit',
  '428': 'configuration',
  '429': 'rate-limit',
  '500': 'server',
  '503': 'server',
  '5XX': 'server',
};

const EXISTING_ERROR_KEY = {
  'hubspot': new Set(['401', '429']),
  'activecampaign': new Set(['400']),
  'salesforce': new Set(['INVALID_SESSION_ID']),
};

function deriveCode(rawCode) {
  if (!rawCode) return 'UNKNOWN';
  const cleaned = rawCode.trim();
  if (cleaned === '5XX') return '500';
  if (/^\d{3}$/.test(cleaned)) return cleaned;
  if (cleaned.startsWith('4') && cleaned.length > 3) return cleaned.split(' ')[0];
  if (cleaned.startsWith('5') && cleaned.length > 3) return cleaned.split(' ')[0];
  return cleaned.toUpperCase().replace(/[\s-]+/g, '_');
}

function normalizeErrorCode(rawCode) {
  if (/^\d{3}$/.test(rawCode.trim())) return rawCode.trim();
  if (rawCode.includes('400')) return '400';
  if (rawCode.includes('401')) return '401';
  if (rawCode.includes('402')) return '402';
  if (rawCode.includes('403')) return '403';
  if (rawCode.includes('404')) return '404';
  if (rawCode.includes('409')) return '409';
  if (rawCode.includes('410')) return '410';
  if (rawCode.includes('413')) return '413';
  if (rawCode.includes('414')) return '414';
  if (rawCode.includes('415')) return '415';
  if (rawCode.includes('420')) return '420';
  if (rawCode.includes('422')) return '422';
  if (rawCode.includes('423')) return '423';
  if (rawCode.includes('428')) return '428';
  if (rawCode.includes('429')) return '429';
  if (rawCode.includes('500')) return '500';
  if (rawCode.includes('503')) return '503';
  if (rawCode.includes('5XX')) return '500';
  return rawCode;
}

function generateSlug(errorCode) {
  const code = normalizeErrorCode(errorCode);
  if (/^\d{3}$/.test(code)) return `errors-${code}`;
  const clean = errorCode.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  return `errors-${clean}`;
}

function generateTitle(toolName, errorCode, description) {
  const code = normalizeErrorCode(errorCode);
  const firstBit = description.split('.')[0].split('—')[0].trim();
  const shortDesc = firstBit.length > 60 ? firstBit.slice(0, 57) + '...' : firstBit;
  return `${toolName} API ${code}: ${shortDesc}`;
}

function generateDescription(toolName, errorCode, description, solution) {
  const code = normalizeErrorCode(errorCode);
  const desc = description.split('.')[0].trim();
  const sol = solution.split('.')[0].trim();
  return `Fix ${toolName} API ${code} ${errorCode !== code ? `(${errorCode}) ` : ''}error. ${desc}. ${sol}.`;
}

function generateKeywords(toolName, toolSlug, errorCode, description) {
  const code = normalizeErrorCode(errorCode);
  const words = [
    `${toolSlug} api ${code} error`,
    `${toolSlug} ${code} fix`,
    `${toolSlug} api ${description.split(' ').slice(0, 4).join(' ').toLowerCase()}`,
  ];
  if (Number(code)) {
    words.push(`${toolSlug} http ${code}`);
  }
  return words;
}

function escapeYaml(str) {
  if (!str) return '';
  const escaped = str.replace(/"/g, '\\"');
  if (escaped.includes('\n') || escaped.includes(':') || escaped.includes('#') || escaped.length > 50) {
    return `"${escaped}"`;
  }
  return `"${escaped}"`;
}

function generateFrontmatter(toolId, rawCode, description, solution) {
  const toolName = TOOL_DISPLAY[toolId] || toolId;
  const errorCode = normalizeErrorCode(rawCode);
  const slug = generateSlug(rawCode);
  const category = CATEGORY_MAP[errorCode] || 'unknown';
  const severity = SEVERITY_MAP[errorCode] || 'medium';
  const priority = severity === 'high' || severity === 'critical' ? 1 : 2;

  const lines = ['---'];
  lines.push(`layout: "../../layouts/ErrorCodeLayout.astro"`);
  lines.push(`title: ${escapeYaml(generateTitle(toolName, rawCode, description))}`);
  lines.push(`description: ${escapeYaml(generateDescription(toolName, rawCode, description, solution))}`);
  lines.push(`tool: "${toolId}"`);
  lines.push(`errorCode: "${errorCode}"`);
  lines.push(`errorName: "${rawCode}"`);
  lines.push(`httpStatus: ${Number(errorCode) || 0}`);
  lines.push(`category: "${category}"`);
  lines.push(`severity: "${severity}"`);
  lines.push(`priority: ${priority}`);
  lines.push(`lastUpdated: "2026-06-29"`);
  lines.push(`lastReviewed: "2026-06-29"`);
  lines.push(`pageType: "error-code"`);
  lines.push(`author: "API Integration Hub"`);
  lines.push('keywords:');
  const keywords = generateKeywords(toolName, toolId, rawCode, description);
  for (const kw of keywords.slice(0, 5)) {
    lines.push(`  - "${kw}"`);
  }
  lines.push('---');
  return lines.join('\n');
}

function generateBody(toolName, rawCode, description, solution) {
  const errorCode = normalizeErrorCode(rawCode);
  const sections = [];

  // What causes
  sections.push(`## What Causes ${toolName} ${errorCode}`);
  sections.push('');
  sections.push(description);
  sections.push('');

  // Step-by-Step Fix
  sections.push('## Step-by-Step Fix');
  sections.push('');
  if (solution && solution.length > 10) {
    sections.push('1. ' + solution.split('.')[0].trim() + '.');
    sections.push('');
    if (solution.includes('. ') && solution.split('. ').length > 1) {
      const steps = solution.split('. ').filter(s => s.trim().length > 5);
      steps.slice(1).forEach((step, i) => {
        sections.push(`${i + 2}. ${step.trim()}.`);
        sections.push('');
      });
    } else {
      sections.push('2. Test with a single record before bulk operations.');
      sections.push('');
      sections.push('3. Monitor error logs for this specific error code.');
      sections.push('');
    }
  } else {
    sections.push('1. Identify the specific error message from the API response.');
    sections.push('');
    sections.push('2. Check the official API documentation for this error.');
    sections.push('');
    sections.push('3. Test with a single record before bulk operations.');
    sections.push('');
  }

  // Prevention
  sections.push('## Prevention');
  sections.push('');
  const preventions = [
    '- Test all API operations in a sandbox environment before production.',
    '- Monitor error logs and set up alerts for this error code.',
    '- Keep API client libraries up to date with the latest versions.',
    '- Implement proper error handling with retry logic.',
  ];
  sections.push(preventions.join('\n'));
  sections.push('');

  // Official Documentation
  sections.push('## Official Documentation');
  sections.push('');
  const docUrls = {
    hubspot: 'https://developers.hubspot.com/docs/api/overview',
    salesforce: 'https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/',
    activecampaign: 'https://developers.activecampaign.com/reference/overview',
    pipedrive: 'https://developers.pipedrive.com/docs/api/v1',
    mailchimp: 'https://mailchimp.com/developer/marketing/api/',
    slack: 'https://api.slack.com/',
    zoho: 'https://www.zoho.com/crm/developer/docs/api/v3/',
    calendly: 'https://developer.calendly.com/api-docs/',
    make: 'https://www.make.com/en/api-documentation',
    zapier: 'https://platform.zapier.com/',
  };
  const docUrl = docUrls[toolName.toLowerCase().replace(/\s*\(.*\)/, '')] || '#';
  sections.push(`- [${toolName} API Documentation](${docUrl})`);
  sections.push('');

  // Related Errors
  sections.push('## Related Errors');
  sections.push('');

  return sections.join('\n');
}

async function main() {
  const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('-api-data.json'));
  let generated = 0;
  let skipped = 0;

  for (const file of files) {
    const data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf-8'));
    const toolId = data.tool_id;
    if (!toolId || !TOOL_TO_SLUG[toolId]) continue;

    const errors = data.error_dictionary || data.errors || [];
    const toolName = TOOL_DISPLAY[toolId] || toolId;
    const toolDir = path.join(CONTENT_DIR, toolId);
    if (!fs.existsSync(toolDir)) fs.mkdirSync(toolDir, { recursive: true });

    const existing = EXISTING_ERROR_KEY[toolId] || new Set();

    for (const err of errors) {
      const rawCode = (err.error_code || err.code || 'UNKNOWN').toString().trim();
      const existingCode = err.error_code ? normalizeErrorCode(err.error_code.toString()) : normalizeErrorCode(rawCode);
      
      if (existing.has(existingCode)) {
        skipped++;
        continue;
      }

      const description = err.description || err.cause || err.message || '';
      const solution = err.solution || err.solution_summary || err.fix || '';
      if (!description && !solution) continue;

      const slug = generateSlug(rawCode);
      const filename = `${slug}.md`;
      const filepath = path.join(toolDir, filename);

      if (fs.existsSync(filepath)) {
        skipped++;
        continue;
      }

      const frontmatter = generateFrontmatter(toolId, rawCode, description, solution);
      const body = generateBody(toolName, rawCode, description, solution);
      const content = frontmatter + '\n\n' + body;

      fs.writeFileSync(filepath, content, 'utf-8');
      console.log(`Generated: ${toolId}/${filename}`);
      generated++;
    }
  }

  console.log(`\nDone. Generated ${generated} new error pages, skipped ${skipped} existing.`);
}

main().catch(err => { console.error(err); process.exit(1); });
