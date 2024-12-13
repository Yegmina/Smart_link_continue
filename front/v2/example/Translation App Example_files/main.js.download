document.getElementById("process-button").addEventListener("click", async () => {
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");
    const userInput = document.getElementById("textInput").value.trim(); // Capture user input from textarea

    console.debug("DEBUG: Process button clicked");

    loadingDiv.style.display = "block"; // Show loading indicator
    resultsDiv.innerHTML = ""; // Clear previous results
    console.debug("DEBUG: Cleared previous results and displayed loading indicator");

    try {
        // Fetch the JSON data from the server
        console.debug("DEBUG: Fetching JSON data from the server");
        const response = await fetch("http://127.0.0.1:5000/scraped_companies");
        if (!response.ok) {
            throw new Error(`Failed to fetch JSON data: ${response.statusText}`);
        }
        const jsonData = await response.json();
        console.debug("DEBUG: Successfully fetched JSON data:", jsonData);

        const companies = jsonData.data || {};
        console.debug("DEBUG: Companies data:", companies);

        // Prepare data to send to /process endpoint
        const payload = {
            userInput, // Add the user input from the textarea
            companies, // Include the companies data
        };
        console.debug("DEBUG: Data to send to /process endpoint:", payload);

        // Send the data to the /process endpoint
        const processResponse = await fetch("http://127.0.0.1:5000/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        console.debug("DEBUG: Fetch request sent to /process endpoint");

        if (!processResponse.body) {
            console.error("DEBUG: No response body from /process endpoint");
            throw new Error("No response body");
        }

        console.debug("DEBUG: Server response received from /process endpoint, starting to read response body stream");
        const reader = processResponse.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let receivedText = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                console.debug("DEBUG: Stream reading completed");
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            console.debug("DEBUG: Chunk received from server:", chunk);

            receivedText += chunk;

            // Try to parse the JSON when it's complete
            let partialData;
            try {
                partialData = JSON.parse(receivedText);
            } catch (err) {
                console.debug("DEBUG: Incomplete JSON chunk, waiting for more data");
                continue; // Wait for more chunks
            }

            console.debug("DEBUG: Parsed partial data successfully", partialData);
            updateResults(partialData.results);
        }

        loadingDiv.style.display = "none"; // Hide loading indicator
        console.debug("DEBUG: Loading indicator hidden, process completed");
    } catch (err) {
        loadingDiv.style.display = "none"; // Hide loading indicator
        console.error("DEBUG: Error during processing", err);
        alert("Failed to process the data. Check the console for details.");
    }
});

/**
 * Updates the results display with processed company data.
 * @param {Array} results - Array of company data objects.
 */
function updateResults(results) {
    const resultsDiv = document.getElementById("results");

    results.forEach((item) => {
        console.debug("DEBUG: Appending company data to resultsDiv", item);

        if (document.querySelector(`[data-company="${item.company_name}"]`)) return;

        const companyDiv = document.createElement("div");
        companyDiv.setAttribute("data-company", item.company_name);
        companyDiv.innerHTML = `
            <h2>${item.company_name}</h2>
            <p>${item.analysis}</p>
            <p>${item.sales_leads}</p>
            <p><strong>Partnership Probability:</strong> ${item.partnership_probability}%</p>
        `;
        resultsDiv.appendChild(companyDiv);
    });
}

