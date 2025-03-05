'use client';
import { useParams } from 'next/navigation';
import FullBillView from '@/components/FullBillView';
import Charts from '@/components/Charts';



export default function BillPage() {
  const params = useParams();
  const billId = params.id as string;

 
  return (
    <>
      <FullBillView billId={billId} />
      <Charts billId={billId} />
</> )
}
