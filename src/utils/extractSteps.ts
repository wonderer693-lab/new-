export interface HowToStep {
  name: string;
  text: string;
}

export function extractSteps(markdownBody: string): HowToStep[] {
  const stepMatch = markdownBody.match(/## Step-by-Step Fix\s*\n([\s\S]*?)(?=\n## |\n---|\s*$)/);
  if (!stepMatch) return [];

  const section = stepMatch[1];
  const steps: HowToStep[] = [];
  const lines = section.split('\n');

  let currentStep = '';
  let currentText = '';

  for (const line of lines) {
    const stepMatch = line.match(/^###\s+(\d+)\.\s+(.+)/);
    if (stepMatch) {
      if (currentStep && currentText) {
        steps.push({ name: currentStep, text: currentText.trim() });
      }
      currentStep = stepMatch[2];
      currentText = '';
    } else if (currentStep && line.trim() && !line.startsWith('```')) {
      currentText += line.trim() + ' ';
    }
  }

  if (currentStep && currentText) {
    steps.push({ name: currentStep, text: currentText.trim() });
  }

  return steps;
}
