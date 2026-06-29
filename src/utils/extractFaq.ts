export interface FaqItem {
  question: string;
  answer: string;
}

export function extractFaq(markdownBody: string): FaqItem[] {
  const paaMatch = markdownBody.match(/## People Also Ask\s*\n([\s\S]*?)(?=\n## |\n---|\s*$)/);
  if (!paaMatch) return [];

  const section = paaMatch[1];
  const items: FaqItem[] = [];
  const lines = section.split('\n');

  for (const line of lines) {
    const qaMatch = line.match(/^-\s+\*\*(.+?)\*\*\s*(.+)/);
    if (qaMatch) {
      items.push({ question: qaMatch[1].replace(/\?$/, '') + '?', answer: qaMatch[2].trim() });
    }
  }

  return items;
}
