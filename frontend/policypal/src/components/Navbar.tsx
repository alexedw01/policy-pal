'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import SearchBar from './SearchBar';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useUser();

  return (
    <nav className="flex items-center justify-between p-4">
      <div className="flex items-center space-x-8">
        <Link href="/" className="text-2xl font-bold text-white">
          Policy Pal
        </Link>
        <div className="hidden md:flex space-x-6">
          <Link 
            href="/"
            className={`text-white hover:text-blue-200 ${pathname === '/' ? 'text-blue-200' : ''}`}
          >
            Home
          </Link>
          <Link 
            href="/trending"
            className={`text-white hover:text-blue-200 ${pathname === '/trending' ? 'text-blue-200' : ''}`}
          >
            Trending
          </Link>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <SearchBar />
        {isAuthenticated ? (
          <div className="flex items-center space-x-4">
            <span className="text-white">Welcome, {user?.username}</span>
            <button
              onClick={logout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link
            href="/auth"
            className="bg-white text-blue-600 px-4 py-2 rounded hover:bg-blue-50"
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}