import React from 'react';
import { useLocation } from 'react-router-dom';

const SearchResults = () => {
    const location = useLocation();
    const { results } = location.state || {};

    return (
        // TODO: update styles to reflect markup
        <div>
            <h1>Search Results</h1>
            <div id="results-container">
                {results ? (
                    results.map((result, index) => (
                        <div key={index} className="result-item">
                            <h3><a href={result.link}>{result.title}</a></h3>
                            <p><strong>Sponsor:</strong> {result.sponsor}</p>
                            <p><strong>Committees:</strong> {result.committees}</p>
                            <p><strong>Latest Action:</strong> {result.latestAction}</p>
                        </div>
                    ))
                ) : (
                    <p>No results available.</p>
                )}
            </div>
        </div>
    );
};

export default SearchResults;
