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
    upvote_count: number;
    created_at: string;
}