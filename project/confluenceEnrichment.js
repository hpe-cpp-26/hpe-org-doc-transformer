const express = require('express');
const axios = require('axios');
require("dotenv").config();

const app = express();
app.use(express.json());

const BASE_URL = process.env.CONFLUENCE_BASE_URL;
const EMAIL = process.env.CONFLUENCE_EMAIL;
const API_TOKEN = process.env.CONFLUENCE_API_TOKEN;

function cleanHTML(html) {
  return html.replace(/<[^>]+>/g, '').trim();
}

async function fetchPage(pageId, version = null) {
  const url = version
    ? `${BASE_URL}/wiki/rest/api/content/${pageId}?expand=body.storage&version=${version}`
    : `${BASE_URL}/wiki/rest/api/content/${pageId}?expand=body.storage,version`;

  const res = await axios.get(url, {
    auth: {
      username: EMAIL,
      password: API_TOKEN,
    },
  });

  return res.data;
}

app.post("/enrich/confluence", async (req, res) => {
  const { pageId } = req.body;

  if (!pageId) {
    return res.status(400).json({ error: "pageId required" });
  }

  try {
    console.log("=================================");
    console.log("Fetching Confluence page:", pageId);

    const currentPage = await fetchPage(pageId);
    const currentVersion = currentPage.version.number;

    const newContent = cleanHTML(currentPage.body.storage.value);

    console.log("Current Version:", currentVersion);
    console.log("New Content:", newContent);

    let oldContent = null;

    if (currentVersion > 1) {
      try {
        const prevPage = await fetchPage(pageId, currentVersion - 1);
        oldContent = cleanHTML(prevPage.body.storage.value);
      } catch (err) {
        console.log("Previous version fetch failed:", err.message);
      }
    }

    console.log("Previous Content:", oldContent);

    const contentChanged = oldContent !== newContent;

    console.log("Content Changed:", contentChanged);
    console.log("=================================");

    res.json({
      pageDetails: {
        id: currentPage.id,
        title: currentPage.title,
        version: currentVersion,
        content: newContent,
        summary: newContent.slice(0, 200),
        changes: contentChanged
          ? {
              from: oldContent,
              to: newContent,
            }
          : null,
      },
    });

  } catch (err) {
    console.error("Confluence enrichment failed:", err.response?.data || err.message);
    res.status(500).json({ error: "Confluence enrichment failed" });
  }
});

app.listen(5001, () => {
  console.log("Confluence enrichment service running on port 5001");
});