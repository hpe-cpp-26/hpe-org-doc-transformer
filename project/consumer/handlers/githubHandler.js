const axios = require("axios");
require("dotenv").config({
  path: require("path").resolve(__dirname, "../../.env"),
});

const { hasChanged } = require("../hashStore");
const { extractReadmeData } = require("../utils/readmeParser");

module.exports = async function (data, channel) {
  const { payload } = data;

  const repo = payload.repository?.full_name;

  console.log("Repo received:", repo);

  if (!repo) {
    console.log("Invalid Github payload");
    return;
  }

  try {
    console.log("Calling API for full details");

    const response = await axios.post(
      "http://localhost:4000/enrich/github",
      { repo }
    );

    console.log(
      "ENRICHMENT RESPONSE:",
      Object.keys(response.data)
    );

    const repoDetails = response.data.repoDetails;
    const readme = response.data.readme;

    console.log("=================================");
    console.log(
      "README RECEIVED IN HANDLER:",
      readme?.slice(0, 100)
    );
    console.log("=================================");

    const parsed = extractReadmeData(readme);

    console.log("PARSED README:", parsed);

    const commits = payload.commits || [];
    let commitDetails = [];

    for (const commit of commits) {
      try {
        console.log("Fetching commit:", commit.id);

        const commitRes = await axios.get(
          `https://api.github.com/repos/${repo}/commits/${commit.id}`,
          {
            headers: process.env.GITHUB_TOKEN
              ? {
                  Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
                }
              : {},
          }
        );

        const files = (commitRes.data.files || [])
          .filter((file) => {
            const filename = file.filename.toLowerCase();

            const isImportantDoc =
              filename.includes("readme") ||
              filename.endsWith(".md") ||
              filename.includes("docs") ||
              filename.endsWith("package.json") ||
              filename.endsWith("docker-compose.yml") ||
              filename.endsWith(".yaml") ||
              filename.endsWith(".yml");

            const isSmallPatch =
              file.patch && file.patch.length < 1000;

            return isImportantDoc || isSmallPatch;
          })
          .map((file) => {
            const filename = file.filename.toLowerCase();
          
            return {
              filename: file.filename,
              status: file.status,
              additions: file.additions,
              deletions: file.deletions,
              changes: file.changes,
          
              
              patch: filename.includes("readme")
                ? null
                : file.patch
                  ? file.patch.slice(0, 1000)
                  : null,
            };
          });

        if (files.length === 0) {
          console.log(
            "No important file changes found for commit:",
            commit.id
          );
          continue;
        }

        commitDetails.push({
          commitId: commit.id,
          message: commit.message,
          author: commit.author?.name || null,
          timestamp: commit.timestamp || null,
          files,
        });

      } catch (err) {
        console.log(
          "Commit fetch failed:",
          err.response?.data || err.message
        );
      }
    }

    console.log(
      "Commit Details:",
      JSON.stringify(commitDetails, null, 2)
    );

    const fullData = {
      repo,
      name: repoDetails.name,
      description: repoDetails.description,

      readmeSummary: parsed.description || "",
      features: parsed.features || [],

      commits: commitDetails,
    };

    console.log(
      "FINAL DATA GOING TO QUEUE:",
      JSON.stringify(fullData, null, 2)
    );

    if (!hasChanged(repo, fullData)) {
      console.log("Github data has not changed");
      return;
    }

    channel.sendToQueue(
      "normalization_queue",
      Buffer.from(
        JSON.stringify({
          source: "github",
          payload,
          fullData,
        })
      ),
      { persistent: true }
    );

    console.log("Github sent to Normalization_Queue");

  } catch (err) {
    console.log(
      "Github error:",
      err.response?.data || err.message
    );
  }
};