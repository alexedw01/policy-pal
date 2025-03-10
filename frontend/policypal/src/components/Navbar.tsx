'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import SearchBar from './SearchBar';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useUser();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen(!menuOpen);

  return (
    <nav className="relative flex items-center justify-between p-4 bg-blue-600">
      <div className="flex items-center space-x-4">
        <button
          className="md:hidden text-white focus:outline-none"
          onClick={toggleMenu}
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
        <Link href="/" className="text-2xl font-bold text-white">
          Policy Pal
        </Link>
        <div className="hidden md:flex space-x-6">
          <Link 
            href="/search-adv"
            className={`text-white hover:text-blue-200 ${pathname === '/search-adv' ? 'text-blue-200' : ''}`}
          >
            Advanced Search
          </Link>
          <Link 
            href="/trending"
            className={`text-white hover:text-blue-200 ${pathname === '/trending' ? 'text-blue-200' : ''}`}
          >
            Trending
          </Link>
          <Link 
            href="/about"
            className={`text-white hover:text-blue-200 ${pathname === '/about' ? 'text-blue-200' : ''}`}
          >
            About
          </Link>
          <Link 
            href="https://vote.gov/"
            className="text-white hover:text-blue-200"
          >
            Register to Vote!
          </Link>
          <Link 
            href="https://www.usa.gov/elected-officials"
            className="text-white hover:text-blue-200"
          >
            Contact Representatives!
          </Link>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <SearchBar />
        {isAuthenticated ? (
          <div className="hidden md:flex items-center space-x-4">
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
      
      {/* Mobile dropdown menu */}
      {menuOpen && (
        <div className="absolute top-full left-0 w-full bg-blue-600 md:hidden">
          <div className="flex flex-col space-y-2 p-4">
            <Link 
              href="/"
              className={`text-white hover:text-blue-200 ${pathname === '/' ? 'text-blue-200' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              href="/trending"
              className={`text-white hover:text-blue-200 ${pathname === '/trending' ? 'text-blue-200' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              Trending
            </Link>
            <Link 
              href="/about"
              className={`text-white hover:text-blue-200 ${pathname === '/about' ? 'text-blue-200' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              About
            </Link>
            <Link 
              href="https://vote.gov/"
              className="text-white hover:text-blue-200"
              onClick={() => setMenuOpen(false)}
            >
              Register to Vote!
            </Link>
            <Link 
              href="https://www.usa.gov/elected-officials"
              className="text-white hover:text-blue-200"
              onClick={() => setMenuOpen(false)}
            >
              Contact Representatives!
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
