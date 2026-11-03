import { notFound } from 'next/navigation';
import { Workspace } from '@/components/workspace';
export default async function StagePage({ params }: { params: Promise<{ stage: string }> }) {
  const { stage } = await params;
  if (!['verify','overview','analysis','cycles','conclusion'].includes(stage)) notFound();
  return <Workspace stage={stage}/>;
}
