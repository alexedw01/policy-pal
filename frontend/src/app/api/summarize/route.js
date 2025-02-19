// app/api/summarize/route.js
export async function GET(request) {
    try {
      // Retrieve the API key from your environment variables.
      const apiKey = process.env.CONGRESS_API_KEY;
      console.log("trying now!");
      if (!apiKey) {
        return new Response(JSON.stringify({ error: "API key not set" }), { status: 500 });
      }
  
      // Fetch data from the congress.gov API.
      const congressResponse = await fetch(`https://api.congress.gov/v3/bill/117/hr/3076/text?api_key=${apiKey}`);
      if (!congressResponse.ok) {
        console.log("YIKES");
        throw new Error("Failed to fetch data from congress.gov");
      }
      
      const data = await congressResponse.json();
      console.log(data)
      // Look for the text version with type "Enrolled Bill" and "Formatted Text".
      let formattedTextUrl = null;
      for (const version of data.textVersions) {
        if (version.type === "Enrolled Bill") {
          const formatObj = version.formats.find((f) => f.type === "Formatted Text");
          if (formatObj) {
            formattedTextUrl = formatObj.url;
            break;
          }
        }
      }
  
      if (!formattedTextUrl) {
        return new Response(JSON.stringify({ error: "Formatted Text URL not found" }), { status: 404 });
      }
  
      // Fetch the formatted HTML page.
      const textResponse = await fetch(formattedTextUrl);
      if (!textResponse.ok) {
        throw new Error("Failed to fetch the formatted text page");
      }
      const htmlText = await textResponse.text();
  
      // Extract text within the <pre> tag.
      const preMatch = htmlText.match(/<pre[^>]*>([\s\S]*?)<\/pre>/i);
      const extractedText = preMatch ? preMatch[1].trim() : "";
  
      return new Response(JSON.stringify({ summary: extractedText }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), { status: 500 });
    }
  }
  