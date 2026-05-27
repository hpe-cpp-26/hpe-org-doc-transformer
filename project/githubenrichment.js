const express = require("express");
const axios = require("axios");

require("dotenv").config();

const app = express();

app.use(express.json());

app.post(
  "/enrich/github",
  async (req, res) => {

    const {
      repo,
      changedFiles,
    } = req.body;

    if (!repo) {

      return res.status(400).json({
        error: "repo is required",
      });
    }

    try {

      const repoRes =
        await axios.get(
          `https://api.github.com/repos/${repo}`,
          {
            headers:
              process.env.GITHUB_TOKEN
                ? {
                    Authorization:
                      `Bearer ${process.env.GITHUB_TOKEN}`,
                  }
                : {},
          }
        );

      const readmeFiles =
        (changedFiles || []).filter(
          (file) => {

            const lower =
              file.toLowerCase();

            return (

              lower.includes(
                "readme"
              ) ||

              lower.endsWith(
                ".md"
              ) ||

              lower.includes(
                "docs"
              )
            );
          }
        );

      console.log(
        "Changed README/doc files:",
        readmeFiles
      );

      let readmeContents = [];

      for (const file of readmeFiles) {

        try {

          const contentRes =
            await axios.get(
              `https://api.github.com/repos/${repo}/contents/${file}`,
              {
                headers: {

                  ...(process.env.GITHUB_TOKEN
                    ? {
                        Authorization:
                          `Bearer ${process.env.GITHUB_TOKEN}`,
                      }
                    : {}),

                  Accept:
                    "application/vnd.github.v3+json",
                },
              }
            );

          if (
            !contentRes.data ||
            !contentRes.data.content
          ) {

            console.log(
              `No content found for file: ${file}`
            );

            continue;
          }

          const decoded =
            Buffer.from(
              contentRes.data.content,
              "base64"
            ).toString("utf-8");

          readmeContents.push({

            file,

            content: decoded,
          });

        } catch (err) {

          console.log(
            `Failed fetching ${file}:`,
            err.response?.data ||
              err.message
          );
        }
      }

      console.log(
        "Total README contents fetched:",
        readmeContents.length
      );

      res.json({

        repoDetails:
          repoRes.data,

        readme:
          readmeContents,
      });

    } catch (err) {

      console.error(
        "Enrichment Failed:",
        err.response?.data ||
          err.message
      );

      res.status(500).json({
        error:
          "Failed to enrich data",
      });
    }
  }
);

app.listen(4000, () => {

  console.log(
    "Github enrichment service running on port 4000"
  );
});