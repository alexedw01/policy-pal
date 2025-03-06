'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Bill } from '@/types/bill';
import { useUser } from '@/contexts/UserContext';
// import { upvoteBill } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import VoteButton from './VoteButton';

interface BillCardProps {
  bill: Bill;
}

export default function BillCard({ bill }: BillCardProps) {
 // const [upvotes, setUpvotes] = useState(bill.upvote_count);
 // const [hasUpvoted, setHasUpvoted] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const { user } = useUser();
  const router = useRouter();

 /* const handleUpvote = async () => {
    if (!user) {
      router.push('/auth');
      return;
    }

    try {
      await upvoteBill(bill._id);
      setUpvotes(prev => prev + 1);
      setHasUpvoted(true);
    } catch (error) {
      if (error instanceof Error && error.message === 'Already voted') {
        setHasUpvoted(true);
      } else {
        console.error('Failed to upvote:', error);
      }
    }
  }; */

  const handleViewFull = () => {
    router.push(`/bills/${bill._id}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 hover:text-blue-600 cursor-pointer" onClick={handleViewFull}>
              {bill.title}
            </h2>
            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
              <span>{bill.bill_type}{bill.bill_number}</span>
              <span>•</span>
              <span>{bill.origin_chamber}</span>
              <span>•</span>
              <span>{formatDistanceToNow(new Date(bill.created_at))} ago</span>
            </div>
          </div>

          
          <VoteButton billId={bill._id} initialUpvotes={bill.upvote_count} initialDownvotes={bill.downvote_count} />
        </div> 

        {bill.ai_summary && (
          <div className="mt-4">
            <p className={`text-gray-700 ${isExpanded ? '' : 'line-clamp-3'}`}>
              {bill.ai_summary}
            </p>
            {bill.ai_summary.length > 200 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
              >
                {isExpanded ? 'Show less' : 'Read more'}
              </button>
            )}
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            <span className="font-medium">Latest Action:</span>{' '}
            <span>{bill.latest_action.text}</span>
          </div>
          <Link 
            href={`/bills/${bill._id}`}
            className="text-blue-600 hover:text-blue-800"
          >
            View Full Bill
          </Link>
        </div>
      </div>
    </div>
  );
}