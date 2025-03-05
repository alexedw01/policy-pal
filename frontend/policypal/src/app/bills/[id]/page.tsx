'use client';
import { useParams } from 'next/navigation';
import FullBillView from '@/components/FullBillView';

export default function BillPage() {
  const params = useParams();
  const billId = params.id as string;

  return <FullBillView billId={billId} />;
}