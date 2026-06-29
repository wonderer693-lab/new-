import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.join(__dirname, '..', 'public');

const WIDTH = 1200;
const HEIGHT = 630;

function createSvg({ title, subtitle, accent = '#2563eb' }) {
  return `<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a"/>
      <stop offset="50%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    <radialGradient id="glow1" cx="85%" cy="15%" r="30%">
      <stop offset="0%" style="stop-color:${accent};stop-opacity:0.15"/>
      <stop offset="100%" style="stop-color:${accent};stop-opacity:0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="15%" cy="85%" r="25%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.1"/>
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <rect width="100%" height="100%" fill="url(#glow1)"/>
  <rect width="100%" height="100%" fill="url(#glow2)"/>
  <rect x="0" y="0" width="100%" height="4" fill="${accent}" opacity="0.8"/>
  <text x="600" y="240" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="28" fill="#94a3b8" font-weight="400">API Integration Hub</text>
  <text x="600" y="320" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="52" fill="#f1f5f9" font-weight="700" letter-spacing="-1">${title}</text>
  <text x="600" y="390" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="22" fill="#94a3b8" font-weight="400">${subtitle}</text>
  <text x="600" y="560" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="16" fill="#64748b">api-integration-hub.com</text>
</svg>`;
}

const CONFIGS = [
  {
    name: 'og-default.svg',
    title: 'API Integration Hub',
    subtitle: 'Error codes, fixes & migration guides for CRM & automation APIs',
  },
  {
    name: 'og-error.svg',
    title: 'API Error Fix',
    subtitle: 'Root cause analysis, step-by-step fixes & code examples',
    accent: '#f59e0b',
  },
  {
    name: 'og-integration.svg',
    title: 'Integration Guide',
    subtitle: 'Cross-tool integration errors & production-ready fixes',
    accent: '#8b5cf6',
  },
  {
    name: 'og-tool.svg',
    title: 'Tool API Reference',
    subtitle: 'Error codes, authentication & rate limits',
    accent: '#14b8a6',
  },
  {
    name: 'og-migration.svg',
    title: 'Migration Guide',
    subtitle: 'API version upgrades & breaking changes',
    accent: '#ef4444',
  },
];

console.log('Generating OG images as SVG...');
for (const cfg of CONFIGS) {
  const svg = createSvg(cfg);
  const outPath = path.join(OUT_DIR, cfg.name);
  fs.writeFileSync(outPath, svg);
  console.log(`Written: ${cfg.name}`);
}
console.log('Done. Note: Most social platforms prefer PNG. Use satori + sharp to convert SVG to PNG for production.');
