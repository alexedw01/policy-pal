import styled from 'styled-components'
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';

const SearchQuery = () => {

    // Contains all parameters needed for Congress search
    const [queryParams, setQueryParams] = useState({
        source: "all",
        congress: ["118", "119"],
        search: "",
        chamber: "all",
        sort: "relevancy",
    });

    // Upon update of any search fields, update queryParams
    const handleUpdate = (e) => {
        const { name, value } = e.target;

        setQueryParams({
            ...queryParams,
            // if Congress, need to update differently for array formatting
            [name]: name === "congress" ? value.split(",") : value,
        });
    };

    // Nagivation used to navigate out to search results
    const navigate = useNavigate();
    
    // Activates when "Search" button is hit; will send queryParams to searchserver
    // and await scraped search content, then filters only relevant information
    // and displays in '/searchresults'
    const handleSubmit = async (e) => {
        e.preventDefault();
    
        // TODO: pass chamber and sorting as additional parameters for filtration
        // and ordering, update search query in backend
        const { chamber, sort, ...webSearchParams } = queryParams;
    
        console.log("Sending raw queryParams:", webSearchParams);
    
        // Send request to the backend
        const response = await fetch('http://localhost:4000/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: webSearchParams }),
        });
    
        const scrapedContent = await response.text();

        // Parse out all unnecessary information from scraped content
        // TODO: error handling if no search results available (e.g. empty search topic)
        // TODO: error testing (e.g. empty search topic) for robust results
        const parser = new DOMParser();
        const doc = parser.parseFromString(scrapedContent, 'text/html');
        const expandedItems = Array.from(doc.querySelectorAll("ol.basic-search-results-lists li.expanded"))
        .map(li => {
            // TODO: improve sorting of individual result elements to handle different kinds of results
            const result = {
                title: li.querySelector(".result-heading a") ? li.querySelector(".result-heading a").textContent.trim() : '',
                link: li.querySelector(".result-heading a") ? li.querySelector(".result-heading a").href : '',
                sponsor: li.querySelector(".result-item strong + a") ? li.querySelector(".result-item strong + a").textContent.trim() : '',
                committees: li.querySelector(".result-item strong + span") ? li.querySelector(".result-item strong + span").textContent.trim() : '',
                latestAction: li.querySelector(".result-item span strong + a") ? li.querySelector(".result-item span strong + a").textContent.trim() : ''
            };
            return result;
        });

        console.log(expandedItems);
        
        // Display search results on '/searchresults', passing the parsed data
        navigate('/searchresults', { state: { results: expandedItems } });
    };

    // TODO: update styles to have search menu reflect markup
	return (
        <div className="search">
            <form onSubmit={handleSubmit}>
                <input type="text" 
                        placeholder="Search bill topics"
                        name="search"
                        value={queryParams.search}
                        onChange={handleUpdate}
                />
                <input type="submit" value="Search" />
                <br />

                <label for="chamber">Chamber:</label>
                <select name="chamber"
                        id="chamber"
                        value={queryParams.chamber}
                        onChange={handleUpdate}
                >
                    <option value="all">All</option>
                    <option value="senate">Senate</option>
                    <option value="house">House</option>
                </select>

                <label for="congress">Congress:</label>
                <select name="congress"
                        id="congress"
                        value={queryParams.congress}
                        onChange={handleUpdate}
                >
                    <option value={"118,119"}>Current Congress</option>
                    <option value={"all"}>All Congresses</option>
                </select>

                <label for="source">Source:</label>
                <select name="source"
                        id="source"
                        value={queryParams.source}
                        onChange={handleUpdate}
                >
                    <option value="all">All</option>
                    <option value="legislation">Legislation</option>
                    <option value="committee_materials">Committee Materials</option>
                    <option value="congressional_record">Congressional Record</option>
                    <option value="members">Members</option>
                    <option value="nominations">Nominations</option>
                </select>

                <label for="sort">Sort by:</label>
                <select name="sort"
                        id="sort"
                        value={queryParams.sort}
                        onChange={handleUpdate}
                >
                    <option value="relevancy">Relevancy</option>
                    <option value="new_to_old">Newest to Oldest</option>
                    <option value="old_to_new">Oldest to Newest</option>
                </select>
            </form>
        </div>
    )
}

export default SearchQuery;