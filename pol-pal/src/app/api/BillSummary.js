"use client";
import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

const BillSummary = () => {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/summarize")
      .then((res) => {
        //console.log(res.text);
        if (!res.ok) throw new Error("Error fetching summary");
        return res.json();
      })
      .then((data) => {
        setSummary(data.summary);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-gray-100 p-6 rounded shadow">
      {loading ? (
        <p>Loading summary...</p>
      ) : error ? (
        <p className="text-red-500">Error: {error}</p>
      ) : (
        <ReactMarkdown className="my-markdown">{summary}</ReactMarkdown>
      )}
    </div>
  );
};

export default BillSummary;
