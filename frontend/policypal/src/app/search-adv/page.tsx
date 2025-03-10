'use client';
import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { searchBills, searchBillsByRelevancy } from '@/lib/api';
import BillCard from '@/components/BillCard';
import { Bill } from '@/types/bill';

export default function AdvancedSearchPage() {

    const router = useRouter();
    const searchParams = useSearchParams();

    const keyword = searchParams.get('keyword') || '';
    const [inputValue, setInputValue] = useState(keyword || "");
    const [chamber, setChamber] = useState('all');
    const [sortBy, setSortBy] = useState('relevancy');
    let today = new Date();
    const [endDate, setEndDate] = useState(today.toISOString().split('T')[0]);
    today.setDate(today.getDate() - 1);
    const [startDate, setStartDate] = useState(today.toISOString().split('T')[0]);
    const [bills, setBills] = useState<Bill[]>([]);
    const [loading, setLoading] = useState(true);

    // const { user } = useUser();

    useEffect(() => {
        const fetchResults = async() => {
            if (!keyword) return;
        
            let data = [];

            try {
                if (sortBy == "relevancy") {
                    data = await searchBillsByRelevancy(keyword);
                }
                else {
                    data = await searchBills(keyword);
                    data.sort((a, b) => {
                        switch (sortBy) {
                            case 'newest':
                                return new Date(b.latest_action_date).getTime() - new Date(a.latest_action_date).getTime();
                            case 'oldest':
                                return new Date(a.latest_action_date).getTime() - new Date(b.latest_action_date).getTime();
                            case 'most-votes':
                                return b.vote_count - a.vote_count;
                            default:
                                return 0;
                        }
                    });
                }

                if (chamber != "all") {
                    if (chamber == "House")
                        data = data.filter(bill => bill.origin_chamber === "House");
                    else
                        data = data.filter(bill => bill.origin_chamber === "Senate");
                }

                const isWithinRange = (bill: Bill, startDate: string, endDate: string) => {
                    const billDates = [bill.latest_action_date, bill.created_at]
                        .filter(date => date) // Ensure the field exists
                        .map(date => new Date(date).toISOString().split('T')[0]); // Convert & format
                
                    return billDates.some(date => date >= startDate && date <= endDate);
                };
                data = data.filter(bill => isWithinRange(bill, startDate, endDate))

                setBills(data);
                console.log(data);
            }
            finally {
                setLoading(false);
            }
        };

        fetchResults();

    }, [keyword, sortBy, chamber, startDate, endDate]);

    return (
        <div className="max-w-4xl mx-auto px-4">
            <h1 className="text-4xl font-bold text-center text-blue-600 mb-6">
                ADVANCED SEARCH
            </h1>
            <div className="flex flex-col items-center gap-4 mb-6">
                <input
                    type="text"
                    placeholder="Search for bills..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    className="w-full max-w-3xl border border-gray-300 px-4 py-3 text-lg rounded-md shadow-sm text-center text-xl focus:outline-none focus:ring-2 focus:ring-blue-400"
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && inputValue.trim()) {
                            router.push(`?keyword=${inputValue.trim()}`);
                        }
                    }}
                />
    
                <div className="flex flex-wrap justify-center gap-4">
                    <select
                        value={chamber}
                        onChange={(e) => setChamber(e.target.value)}
                        className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring focus:ring-blue-300"
                    >
                        <option value="all">All Chambers</option>
                        <option value="House">House</option>
                        <option value="Senate">Senate</option>
                    </select>
    
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring focus:ring-blue-300"
                    >
                        <option value="relevancy">Relevancy</option>
                        <option value="newest">Newest First</option>
                        <option value="oldest">Oldest First</option>
                        <option value="most-votes">Most Votes</option>
                    </select>
    
                    <div className="flex items-center gap-2">
                        <label className="text-blue-600 font-medium">Start date:</label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            min="1799-01-01"
                            max="2025-12-31"
                            className="rounded-md border border-blue-400 px-3 py-2 text-sm focus:ring focus:ring-blue-300"
                        />
                    </div>
    
                    <div className="flex items-center gap-2">
                        <label className="text-blue-600 font-medium">End date:</label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            min="1799-01-01"
                            max="2025-12-31"
                            className="rounded-md border border-blue-400 px-3 py-2 text-sm focus:ring focus:ring-blue-300"
                        />
                    </div>
                </div>
            </div>
    
            {keyword && (
                <h1 className="text-2xl font-regular text-center mb-8">
                    Search Results for &#34;{keyword}&#34;
                </h1>
            )}
    
            <div className="space-y-6">
                {bills.map((bill) => (
                    <BillCard key={bill._id} bill={bill} />
                ))}
            </div>
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