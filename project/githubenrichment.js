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
   try{

        //Here we go into the default branch
        const defaultBranch = repoRes.data.default_branch;

        //iterate the full repo tree
        const treeRes = await axios.get(
          `https://api.github.com/repos/${repo}/git/trees/${defaultBranch}?recursive=1`,
          {
            headers : process.env.GITHUB_TOKEN
            ?{Authorization : `Bearer ${process.env.GITHUB_TOKEN}`}
            : {}
          }
        );

        const readmeFiles = (treeRes.data.tree || []).filter(file =>
          file.path.toLowerCase().includes("readme")
        );

        console.log("README files found:", 
          readmeFiles.map(f => f.path)
        );

        //get all readme contents and store in array
        let readmeContents = [];

        for(const file of readmeFiles){
          try{

              const contentRes = await axios.get(
                `https://api.github.com/repos/${repo}/contents/${file.path}`,
                {
                  headers : {
                    ...(process.env.GITHUB_TOKEN
                      ? {Authorization : `Bearer ${process.env.GITHUB_TOKEN}`}
                      : {}),
                      Accept : "application/vnd.github.v3+json",
                  },
                }
              );

              const decoded = Buffer.from(
                contentRes.data.content,
                "base64"
              ).toString("utf-8");
              
              readmeContents.push(
                `#FILE: ${file.path}\n${decoded}`
              );
          }
          catch(err)
          {
            console.log(
              `Failed fetching README ${file.path}:`,
              err.message
            )
          }
        }

        //combine the contents from all Readme's
        readmeText = readmeContents.join("\n\n");
   }
   catch(err)
   {
      console.log("Readme discovery failed:",
        err.response?.status || err.message
      );
   }


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