import { Bill } from '@/types/bill';

//const API_BASE = process.env.NEXT_PUBLIC_API_URL;
const API_BASE = "http://127.0.0.1:8080/api";


export async function getBills({
  page = 1,
  per_page = 10,
  chamber,
  sort,
}: {
  page?: number;
  per_page?: number;
  chamber?: string;
  sort?: string;
}): Promise<{ bills: Bill[]; pagination: { pages: number } }> {
  const response = await fetch(
    `${API_BASE}/bills?page=${page}&per_page=${per_page}&chamber=${chamber}&sort=${sort}`
  );
  if (!response.ok) throw new Error("Failed to fetch bills");
  return response.json();
}


export async function getTrendingBills(): Promise<Bill[]> {
  const response = await fetch(`${API_BASE}/bills/trending`);
  if (!response.ok) throw new Error('Failed to fetch trending bills');
  return response.json();
}

export async function searchBills(keyword: string): Promise<Bill[]> {
  const response = await fetch(`${API_BASE}/search?keyword=${encodeURIComponent(keyword)}`);
  if (!response.ok) throw new Error('Failed to search bills');
  return response.json();
}

export async function searchBillsByRelevancy(keyword: string): Promise<Bill[]> {
  const response = await fetch(`${API_BASE}/search_tfidf?keyword=${encodeURIComponent(keyword)}`);
  if (!response.ok) throw new Error('Failed to advanced search bills');
  return response.json();
}

export async function getFullBill(billId: string): Promise<Bill> {
  const response = await fetch(`${API_BASE}/bills/${billId}/full`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch bill details');
  }
  return response.json();
}
export async function voteBill(billId: string, voteStatus: 'upvote' | 'downvote' | 'none'): Promise<any> {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('User not authenticated');
  }
  
  const response = await fetch(`${API_BASE}/bills/${billId}/vote`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ vote_status: voteStatus })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `Failed to ${voteStatus} bill`);
  }
  
  return response.json();
}

export async function upvoteBill(billId: string): Promise<any> {
  return voteBill(billId, 'upvote');
}

export async function downvoteBill(billId: string): Promise<any> {
  return voteBill(billId, 'downvote');
}

export async function removeVote(billId: string): Promise<any> {
  return voteBill(billId, 'none');
}

export async function testConnection() {
  try {
    const response = await fetch(`${API_BASE}/test`);
    return response.ok;
  } catch (error) {
    console.error('API Connection Error:', error);
    return false;
  }
}

export async function getBillDemographics(billId: number): Promise<{ bill_id: number; demographics: any }> {
  const response = await fetch(`${API_BASE}/bills/${billId}/demographics`);
  if (!response.ok) throw new Error('Failed to fetch bill demographics');
  return response.json();
}


