'use client';
import { useState, useEffect } from 'react';
import { getTrendingBills } from "@/lib/api";
import BillCard from "@/components/BillCard";
import { Bill } from "@/types/bill";
//import Navbar from '@/components/Navbar';
import LoadingBills from '@/components/LoadingBills';

export default function TrendingPage() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrendingBills();
  }, []);

  const fetchTrendingBills = async () => {
    setLoading(true);
    try {
      const data = await getTrendingBills();
      setBills(data);
    } catch (error) {
      console.error('Error fetching trending bills:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
     <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Trending Bills</h1>
          </div>

          {loading ? (
            <LoadingBills />
          ) : (
            <div className="space-y-6">
              {bills.length > 0 ? (
                bills.map((bill) => (
                  <BillCard key={bill._id} bill={bill} />
                ))
              ) : (
                <div className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-900">No trending bills</h3>
                  <p className="mt-2 text-gray-500">Check back later for popular legislation</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}