import { useState } from 'react';
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

  const getUserVoteStatus = () => {
    if (!user) return 'none';
    try {
      const votedBills = JSON.parse(localStorage.getItem('votedBills') || '{}');
      return votedBills[billId] || initialVoteStatus;
    } catch {
      return initialVoteStatus;
    }
  };

  const userVoteStatus = getUserVoteStatus();

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    if (!user) {
      router.push('/auth');
      return;
    }

    const newVoteStatus = userVoteStatus === voteType ? 'none' : voteType;
    
    setIsLoading(true);
    
    try {
      await voteBill(billId, newVoteStatus);
      
      const votedBills = JSON.parse(localStorage.getItem('votedBills') || '{}');
      if (newVoteStatus === 'none') {
        delete votedBills[billId];
      } else {
        votedBills[billId] = newVoteStatus;
      }
      localStorage.setItem('votedBills', JSON.stringify(votedBills));
      
      window.location.reload();
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
          userVoteStatus === 'upvote'
            ? 'bg-blue-500 text-white' 
            : user 
              ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to upvote' : undefined}
      >
        <span className="text-lg">↑</span>
        <span className="ml-1">{upvoteCount}</span>
      </button>

      <button
        onClick={() => handleVote('downvote')}
        disabled={isLoading || !user}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          userVoteStatus === 'downvote'
            ? 'bg-red-500 text-white' 
            : user 
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={!user ? 'Login to downvote' : undefined}
      >
        <span className="text-lg">↓</span>
        <span className="ml-1">{downvoteCount}</span>
      </button>
    </div>
  );
}