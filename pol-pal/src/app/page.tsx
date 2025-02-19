// app/page.tsx
"use client";
import React from "react";
import BillSummary from "./api/BillSummary"; // make sure the path is correct

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-3xl font-bold">Policy pal</h1>
      </header>

      <main className="flex-grow p-8 max-w-4xl mx-auto">
        <BillSummary />
      </main>

      <footer className="bg-gray-200 p-4 text-center">
        <p className="text-sm">&copy; {new Date().getFullYear()} Policy pal</p>
      </footer>
    </div>
  );
}
