'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SearchBar() {
  const [keyword, setKeyword] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim()) {
      router.push(`/search?keyword=${encodeURIComponent(keyword)}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="flex items-center">
      <input
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="Search bills..."
        className="px-4 py-2 border rounded-l text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button 
        type="submit" 
        className="px-4 py-2 bg-blue-600 text-white rounded-r hover:bg-blue-700"
      >
        Search
      </button>
    </form>
  );
}