import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { upvoteBill, downvoteBill } from '@/lib/api';

interface VoteButtonProps {
  billId: string;
  initialUpvotes: number;
  initialDownvotes: number;
}

export default function VoteButton({ billId, initialUpvotes, initialDownvotes }: VoteButtonProps) {
  const [upvotes, setUpvotes] = useState(initialUpvotes);
  const [downvotes, setDownvotes] = useState(initialDownvotes);
  const [hasVoted, setHasVoted] = useState(false);
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    // Check if the user has already voted on this bill
    // This logic depends on how you store the user's votes
  }, [billId, user]);

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    if (!user) {
      router.push('/auth');
      return;
    }

    try {
      if (voteType === 'upvote') {
        await upvoteBill(billId);
        setUpvotes(prev => prev + 1);
      } else {
        await downvoteBill(billId);
        setDownvotes(prev => prev + 1);
      }
      setHasVoted(true);
    } catch (error) {
      console.error(`Failed to ${voteType}:`, error);
    }
  };

  return (
    <div className="flex space-x-2">
      <button
        onClick={() => handleVote('upvote')}
        disabled={hasVoted || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          hasVoted
            ? 'bg-gray-100 text-gray-500'
            : user 
              ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to upvote' : undefined}
      >
        <span className="text-lg">↑</span>
        <span>{upvotes}</span>
      </button>
      <button
        onClick={() => handleVote('downvote')}
        disabled={hasVoted || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          hasVoted
            ? 'bg-gray-100 text-gray-500'
            : user 
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to downvote' : undefined}
      >
        <span className="text-lg">↓</span>
        <span>{downvotes}</span>
      </button>
    </div>
  );
}