const express = require('express');
const axios = require('axios');
require("dotenv").config();

const app = express();
app.use(express.json());

const Jira_Base_URL = process.env.JIRA_BASE_URL;
const Jira_Email = process.env.JIRA_EMAIL;
const Jira_API_Token = process.env.JIRA_API_TOKEN;



app.post("/enrich/jira" , async(req , res) =>{
    const {issueKey} = req.body;
    if(!issueKey){
        return res.status(400).json({error : "issueKey required"});
    }

    try{
        const issueRes = await axios.get(
            `${Jira_Base_URL}/rest/api/3/issue/${issueKey}`,
            {
                auth:{
                    username : Jira_Email,
                    password : Jira_API_Token,
                },
            }
        );

        const issue = issueRes.data;
        res.json({
            issueDetails : issue
        });
    }
    catch(err){
        console.error("FULL ERROR:");
        console.log(err.response?.status);
        console.log(err.response?.data);
        console.log(err.message);
      }
});

app.listen(5000 , () =>{
    console.log("jira enrichment service running on port 5000");
});