'use client';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { searchBills } from '@/lib/api';
import BillCard from '@/components/BillCard';
import { Bill } from '@/types/bill';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const keyword = searchParams.get('keyword');
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!keyword) return;
      try {
        const data = await searchBills(keyword);
        setBills(data);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [keyword]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-8">
        Search Results for "{keyword}"
      </h1>
      <div className="space-y-6">
        {bills.map((bill) => (
          <BillCard key={bill._id} bill={bill} />
        ))}
      </div>
    </div>
  );
}