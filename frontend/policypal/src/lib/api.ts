import { Bill } from '@/types/bill';

//const API_BASE = process.env.NEXT_PUBLIC_API_URL;
const API_BASE = "http://localhost:5000/api";

export async function getBills(): Promise<Bill[]> {
  const response = await fetch(`${API_BASE}/bills`);
  if (!response.ok) throw new Error('Failed to fetch bills');
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

export async function getFullBill(billId: string): Promise<Bill> {
  const response = await fetch(`${API_BASE}/bills/${billId}/full`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch bill details');
  }
  return response.json();
}

export async function upvoteBill(billId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/bills/${billId}/upvote`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });
  if (!response.ok) throw new Error('Failed to upvote bill');
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