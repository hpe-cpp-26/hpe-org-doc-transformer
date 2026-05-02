const express = require("express");
const axios = require("axios");
require("dotenv").config();

const app = express();
app.use(express.json());

app.post("/enrich/github", async (req, res) => {
  const { repo } = req.body;

  if (!repo) {
    return res.status(400).json({ error: "repo is required" });
  }

  try {
   
    const repoRes = await axios.get(
      `https://api.github.com/repos/${repo}`,
      {
        headers: process.env.GITHUB_TOKEN
      ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` }
      : {},
      }
    );

    
    let readmeText = "";

    try {
      const readmeRes = await axios.get(
        `https://api.github.com/repos/${repo}/readme`,
        {
          headers: {
            Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
            Accept: "application/vnd.github.v3+json",
          },
        }
      );

      readmeText = Buffer.from(
        readmeRes.data.content,
        "base64"
      ).toString("utf-8");

    } catch (err) {
      console.log("README not found:", err.response?.status);
    }

    
    console.log("=================================");
    console.log("README LENGTH:", readmeText.length);
    console.log("README PREVIEW:", readmeText.slice(0, 100));
    console.log("=================================");

    res.json({
      repoDetails: repoRes.data,
      readme: readmeText,
    });

  } catch (err) {
    console.error("Enrichment Failed:", err.message);
    res.status(500).json({ error: "Failed to enrich data" });
  }
});

app.listen(4000, () => {
  console.log("Github enrichment service running on port 4000");
});