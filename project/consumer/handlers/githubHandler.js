const axios = require("axios");

require("dotenv").config({
  path: require("path").resolve(__dirname, "../../.env"),
});

const {
  hasChanged,
} = require("../hashStore");

const {
  extractReadmeData,
} = require("../utils/readmeParser");

module.exports = async function (
  data,
  channel
) {

  const { payload } = data;

  const repo =
    payload.repository?.full_name;

  console.log(
    "Repo received:",
    repo
  );

  if (!repo) {

    console.log(
      "Invalid Github payload"
    );

    return;
  }

  try {

    const commits =
      payload.commits || [];

    let commitDetails = [];

    let changedReadmeFiles = [];

    for (const commit of commits) {

      try {

        console.log(
          "Fetching commit:",
          commit.id
        );

        const commitRes =
          await axios.get(
            `https://api.github.com/repos/${repo}/commits/${commit.id}`,
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

        const files =
          (commitRes.data.files || [])

            .filter((file) => {

              const filename =
                file.filename.toLowerCase();

              const isImportantDoc =

                filename.includes(
                  "readme"
                ) ||

                filename.endsWith(
                  ".md"
                ) ||

                filename.includes(
                  "docs"
                );

              if (isImportantDoc) {

                changedReadmeFiles.push(
                  file.filename
                );
              }

              return isImportantDoc;
            })

            .map((file) => {

              return {

                filename:
                  file.filename,

                status:
                  file.status,

                additions:
                  file.additions,

                deletions:
                  file.deletions,

                changes:
                  file.changes,

                patch:
                  file.patch
                    ? file.patch.slice(
                        0,
                        1000
                      )
                    : null,
              };
            });

        if (files.length === 0) {

          console.log(
            "No markdown/doc related changes found for commit:",
            commit.id
          );

          continue;
        }

        commitDetails.push({

          commitId: commit.id,

          message:
            commit.message,

          author:
            commit.author?.name ||
            null,

          timestamp:
            commit.timestamp ||
            null,

          files,
        });

      } catch (err) {

        console.log(
          "Commit fetch failed:",
          err.response?.data ||
            err.message
        );
      }
    }

    changedReadmeFiles = [

      ...new Set(
        changedReadmeFiles
      ),
    ];

    console.log(
      "Changed README/doc files:",
      changedReadmeFiles
    );

    console.log(
      "Calling API for selective README enrichment"
    );

    const response =
      await axios.post(
        "http://localhost:4000/enrich/github",
        {
          repo,

          changedFiles:
            changedReadmeFiles,
        }
      );

    console.log(
      "ENRICHMENT RESPONSE:",
      Object.keys(
        response.data
      )
    );

    const repoDetails =
      response.data.repoDetails;

    const readmes =
      response.data.readme || [];

    let changedReadmes = [];

    for (const readmeObj of readmes) {

      const file =
        readmeObj.file;

      const latestContent =
        readmeObj.content;

      console.log(
        `README received for ${file}`
      );

      const parsed =
        extractReadmeData(
          latestContent
        );

      changedReadmes.push({

        file,

        content:
          latestContent,

        parsed,
      });
    }

    console.log(
      "Commit Details:",
      JSON.stringify(
        commitDetails,
        null,
        2
      )
    );

    const fullData = {

      repo,

      name:
        repoDetails.name,

      description:
        repoDetails.description,

      changedReadmes,

      commits:
        commitDetails,
    };

    console.log(
      "FINAL DATA GOING TO QUEUE:",
      JSON.stringify(
        fullData,
        null,
        2
      )
    );

    if (
      !hasChanged(
        repo,
        fullData
      )
    ) {

      console.log(
        "Github data has not changed"
      );

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

    console.log(
      "Github sent to Normalization_Queue"
    );

  } catch (err) {

    console.log(
      "Github error:",
      err.response?.data ||
        err.message
    );
  }
};