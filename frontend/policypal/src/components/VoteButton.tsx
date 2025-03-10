import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { voteBill } from '@/lib/api';

interface VoteButtonProps {
  billId: string;
  upvoteCount?: number;
  downvoteCount?: number;
  initialVoteStatus?: 'upvote' | 'downvote' | 'none';
}

export default function VoteButton({ 
  billId, 
  upvoteCount = 0, 
  downvoteCount = 0,
  initialVoteStatus = 'none' 
}: VoteButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useUser();
  const router = useRouter();

  // Create a namespaced key for each user.
  const getVotedBillsKey = (user: any) => user ? `votedBills_${user.email}` : 'votedBills';

  const getUserVoteStatus = () => {
    if (!user) return 'none';
    try {
      const key = getVotedBillsKey(user);
      const votedBills = JSON.parse(localStorage.getItem(key) || '{}');
      return votedBills[billId] || initialVoteStatus;
    } catch {
      return initialVoteStatus;
    }
  };

  const [localVoteStatus, setLocalVoteStatus] = useState(getUserVoteStatus()); // Initialize local state for the vote status and vote counts
  const [localUpvoteCount, setLocalUpvoteCount] = useState(upvoteCount);
  const [localDownvoteCount, setLocalDownvoteCount] = useState(downvoteCount);

  useEffect(() => { // When the user changes (e.g., logs out), resets the vote status
    if (!user) {
      setLocalVoteStatus('none');
    } else {
      setLocalVoteStatus(getUserVoteStatus());
    }
  }, [user, billId]);

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    if (!user) {
      router.push('/auth');
      return;
    }

    const newVoteStatus = localVoteStatus === voteType ? 'none' : voteType;
    setIsLoading(true);

    try {
      await voteBill(billId, newVoteStatus);
      
      const key = getVotedBillsKey(user);// Update namespaced localStorage.
      const votedBills = JSON.parse(localStorage.getItem(key) || '{}');
      if (newVoteStatus === 'none') {
        delete votedBills[billId];
      } else {
        votedBills[billId] = newVoteStatus;
      }
      localStorage.setItem(key, JSON.stringify(votedBills));
      
      if (localVoteStatus === 'none' && newVoteStatus === 'upvote') {// Update local vote counts based on the change.
        setLocalUpvoteCount(prev => prev + 1);
      } else if (localVoteStatus === 'none' && newVoteStatus === 'downvote') {
        setLocalDownvoteCount(prev => prev + 1);
      } else if (localVoteStatus === 'upvote' && newVoteStatus === 'none') {
        setLocalUpvoteCount(prev => prev - 1);
      } else if (localVoteStatus === 'downvote' && newVoteStatus === 'none') {
        setLocalDownvoteCount(prev => prev - 1);
      } else if (localVoteStatus === 'upvote' && newVoteStatus === 'downvote') {
        setLocalUpvoteCount(prev => prev - 1);
        setLocalDownvoteCount(prev => prev + 1);
      } else if (localVoteStatus === 'downvote' && newVoteStatus === 'upvote') {
        setLocalDownvoteCount(prev => prev - 1);
        setLocalUpvoteCount(prev => prev + 1);
      }

      setLocalVoteStatus(newVoteStatus);
      setIsLoading(false);
    } catch (error) {
      console.error('Error voting:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => handleVote('upvote')}
        disabled={isLoading || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          localVoteStatus === 'upvote'
            ? 'bg-blue-500 text-white' 
            : user 
              ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to upvote' : undefined}
      >
        <span className="text-lg">↑</span>
        <span className="ml-1">{localUpvoteCount}</span>
      </button>

      <button
        onClick={() => handleVote('downvote')}
        disabled={isLoading || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          localVoteStatus === 'downvote'
            ? 'bg-red-500 text-white' 
            : user 
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to downvote' : undefined}
      >
        <span className="text-lg">↓</span>
        <span className="ml-1">{localDownvoteCount}</span>
      </button>
    </div>
  );
}