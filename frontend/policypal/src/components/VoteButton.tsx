import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { voteBill } from '@/lib/api';

interface VoteButtonProps {
  billId: string;
  initialVoteStatus: 'upvote' | 'downvote' | 'none';
}

export default function VoteButton({ billId, initialVoteStatus }: VoteButtonProps) {
  const [voteStatus, setVoteStatus] = useState(initialVoteStatus);
  const { user } = useUser();
  const router = useRouter();

  useEffect(() => {
    // Check if the user has already voted on this bill
    // This logic depends on how you store the user's votes
  }, [billId, user]);

  const handleVote = async (voteType: 'upvote' | 'downvote' | 'none') => {
    if (!user) {
      router.push('/auth');
      return;
    }

    try {
      await voteBill(billId, voteType);
      setVoteStatus(voteType);
    } catch (error) {
      console.error(`Failed to ${voteType}:`, error);
    }
  };

  return (
    <div className="flex space-x-2">
      <button
        onClick={() => handleVote('upvote')}
        disabled={voteStatus === 'upvote' || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          voteStatus === 'upvote'
            ? 'bg-blue-600 text-white'
            : user 
              ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to upvote' : undefined}
      >
        <span className="text-lg">↑</span>
      </button>
      <button
        onClick={() => handleVote('downvote')}
        disabled={voteStatus === 'downvote' || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          voteStatus === 'downvote'
            ? 'bg-red-600 text-white'
            : user 
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to downvote' : undefined}
      >
        <span className="text-lg">↓</span>
      </button>
      {voteStatus !== 'none' && (
        <button
          onClick={() => handleVote('none')}
          className="flex items-center space-x-1 px-3 py-1 rounded-full bg-gray-200 text-gray-600 hover:bg-gray-300"
        >
          <span className="text-lg">✕</span>
        </button>
      )}
    </div>
  );
}