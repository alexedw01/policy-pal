'use client';
import { useState, useEffect } from 'react';
import { getBills } from '@/lib/api';
import BillCard from '@/components/BillCard';
import Navbar from '@/components/Navbar';
import { Bill } from '@/types/bill';
import { useUser } from '@/contexts/UserContext';

export default function Home() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [chamber, setChamber] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const { user } = useUser();

  useEffect(() => {
    fetchBills();
  }, [page, chamber, sortBy]);

  const fetchBills = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getBills({
        page,
        per_page: 10,
        chamber,
        sort: sortBy
      });
      const sortedBills = [...response.bills].sort((a, b) => {
        switch (sortBy) {
          case 'newest':
            return new Date(b.latest_action_date).getTime() - new Date(a.latest_action_date).getTime();
          case 'oldest':
            return new Date(a.latest_action_date).getTime() - new Date(b.latest_action_date).getTime();
          case 'most-upvotes':
            return b.upvote_count - a.upvote_count;
          default:
            return 0;
        }
      });
      setBills(sortedBills);
      setTotalPages(response.pagination.pages);
    } catch (error) {
      console.error('Error fetching bills:', error);
      setError('Failed to load bills. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Latest Bills</h1>
          <div className="flex gap-4">
            <select
              value={chamber}
              onChange={(e) => setChamber(e.target.value)}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="all">All Chambers</option>
              <option value="House">House</option>
              <option value="Senate">Senate</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="most-upvotes">Most Upvotes</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <BillCardSkeleton />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={fetchBills}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-6">
              {bills.map((bill) => (
                <BillCard key={bill._id} bill={bill} />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-8 flex justify-center">
                <nav className="flex items-center gap-2">
                  {[...Array(totalPages)].map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setPage(i + 1)}
                      className={`px-4 py-2 rounded-md ${
                        page === i + 1
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </nav>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

function BillCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/3"></div>
    </div>
  );
}