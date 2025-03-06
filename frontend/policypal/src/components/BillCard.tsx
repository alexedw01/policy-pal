'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Bill } from '@/types/bill';
import { useUser } from '@/contexts/UserContext';
import { formatDistanceToNow } from 'date-fns';
import VoteButton from '@/components/VoteButton';

interface BillCardProps {
  bill: Bill;
}

export default function BillCard({ bill }: BillCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { user } = useUser();
  const router = useRouter();

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

          <VoteButton 
            billId={bill._id} 
            upvoteCount={bill.upvote_count || 0}
            downvoteCount={bill.downvote_count || 0}
            initialVoteStatus={bill.user_vote_status || 'none'}
          />
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