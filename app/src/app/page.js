'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [search, setSearch] = useState('');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <header className="w-full max-w-4xl text-center py-6">
        <h1 className="text-4xl font-bold text-gray-800">CSE Stock Analysis</h1>
        <p className="text-gray-600 mt-2">Predict stock trends with sentiment analysis</p>
      </header>
      
      <main className="w-full max-w-3xl bg-white shadow-md rounded-lg p-6">
        <div className="mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search stocks..."
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link href="/sentiment" className="bg-blue-500 text-white py-3 px-6 rounded-lg text-center hover:bg-blue-600 transition">
            View Sentiment Analysis
          </Link>
          <Link href="/stocks" className="bg-green-500 text-white py-3 px-6 rounded-lg text-center hover:bg-green-600 transition">
            View Stock Data
          </Link>
        </div>
      </main>
      
      <footer className="mt-6 text-gray-500">
        <p>© 2025 CSE Prediction Project</p>
      </footer>
    </div>
  );
}
