const puppeteer = require('puppeteer-extra');
const stealthPlugin = require('puppeteer-extra-plugin-stealth');
const express = require('express');
const cors = require('cors');

puppeteer.use(stealthPlugin());

const app = express();
app.use(express.json());
app.use(cors());

app.post('/scrape', async (req, res) => {
    try {
        const { query } = req.body;
        if (!query) {
            return res.status(400).json({ error: 'Query parameters are required' });
        }

        // Stringify and encode the query in the backend
        const jsonQuery = JSON.stringify(query);
        const uriJSONQuery = encodeURIComponent(jsonQuery);

        const searchURL = `https://www.congress.gov/search?q=${uriJSONQuery}`;
        console.log("Final search URL:", searchURL);

        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();

        await page.goto(searchURL, { waitUntil: 'domcontentloaded' });
        await page.waitForSelector('.basic-search-results-lists', { timeout: 60000 });

        const resultsHTML = await page.evaluate(() => {
            const resultsElement = document.querySelector('.basic-search-results-lists');
            return resultsElement ? resultsElement.outerHTML : null;
        });

        await browser.close();

        if (!resultsHTML) {
            return res.status(404).json({ error: 'Search results not found' });
        }

        res.send(resultsHTML);
    } catch (error) {
        console.error('Scraping error:', error);
        res.status(500).json({ error: 'Scraping failed' });
    }
});

app.listen(4000, () => console.log('Server running on port 4000'));