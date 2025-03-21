export interface Bill {
    _id: string;
    congress: number;
    bill_type: string;
    bill_number: string;
    title: string;
    latest_action_date: string;
    origin_chamber?: string;
    sponsor: string;
    latest_action: {
      actionDate: string;
      text: string;
    };
    update_date: string;
    url: string;
    text_preview?: string;
    full_text?: string;
    ai_summary?: string;
    vote_count: number;      
    upvote_count: number;    
    downvote_count: number;  
    created_at: string;
    upvoted_at?: string;
    user_vote_status?: 'upvote' | 'downvote' | 'none';
  }