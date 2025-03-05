'use client';
import { useState, useEffect } from 'react';
import { Bill } from '@/types/bill';
import VoteButton from './VoteButton';

interface FullBillViewProps {
  billId: string;
}

const cleanBillText = (text: string) => {
  return text
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/\[\[.*?\]\]/g, '') // Remove [[brackets]]
    .replace(/\s+/g, ' ') 
    .trim();
};

export default function FullBillView({ billId }: FullBillViewProps) {
  const [bill, setBill] = useState<Bill | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBill = async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/bills/${billId}/full`);
        if (!response.ok) throw new Error('Failed to fetch bill');
        const data = await response.json();
        setBill(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load bill');
      } finally {
        setLoading(false);
      }
    };

    fetchBill();
  }, [billId]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );

  if (error || !bill) return (
    <div className="text-center py-12">
      <h2 className="text-2xl font-semibold text-gray-600">
        {error || 'Bill not found'}
      </h2>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">{bill.title}</h1>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Bill Information</h3>
              <p className="text-gray-700"><span className="font-medium">Bill ID:</span> {bill.bill_type}{bill.bill_number}</p>
              <p className="text-gray-700"><span className="font-medium">Congress:</span> {bill.congress}</p>
              <p className="text-gray-700"><span className="font-medium">Chamber:</span> {bill.origin_chamber}</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Sponsor</h3>
              <p className="text-gray-700">{bill.sponsor}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Latest Action</h3>
              <p className="text-gray-700">{bill.latest_action.text}</p>
              <p className="text-gray-600 text-sm mt-1">
                Date: {new Date(bill.latest_action.actionDate).toLocaleDateString()}
              </p>
            </div>
            <div>
            <div className="flex items-center space-x-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-900">Status</h3>
                <VoteButton billId={bill._id} initialUpvotes={bill.upvote_count} initialDownvotes={bill.downvote_count} />
              </div>
              <p className="text-gray-700">Upvotes: {bill.upvote_count}</p>
              <p className="text-gray-700">Downvotes: {bill.downvote_count}</p>
            </div>
          </div>
        </div>

        {bill.ai_summary && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">AI Summary</h3>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-gray-700">{bill.ai_summary}</p>
            </div>
          </div>
        )}

        {bill.full_text ? (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">Full Bill Text</h3>
            <div className="bg-gray-50 p-6 rounded-lg overflow-auto max-h-[800px] border border-gray-200">
              <pre className="whitespace-pre-wrap font-mono text-sm text-gray-700 leading-relaxed">
                {cleanBillText(bill.full_text)}
              </pre>
            </div>
          </div>
        ) : bill.text_preview ? (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">Bill Text Preview</h3>
            <div className="bg-gray-50 p-6 rounded-lg overflow-auto max-h-[400px] border border-gray-200">
              <pre className="whitespace-pre-wrap font-mono text-sm text-gray-700 leading-relaxed">
                {cleanBillText(bill.text_preview)}
              </pre>
            </div>
            <p className="mt-4 text-sm text-gray-600 italic">
              * This is a preview. Click &#34;View on Congress.gov&#34; for the full text.
            </p>
          </div>
        ) : null}

        {bill.url && (
          <div className="mt-8">
            <a 
              href={bill.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={(e) => {
                e.preventDefault();
                window.open(bill.url, '_blank', 'noopener,noreferrer');
              }}
            >
              View on Congress.gov
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        )}
      </div>
    </div>
  );
}