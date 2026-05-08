const axios = require("axios");
const { hasChanged } = require("../hashStore");

function cleanHTML(html) {
  return html.replace(/<[^>]+>/g, '').trim();
}

module.exports = async function (data, channel) {
  const { payload } = data;

  const pageId = payload.page?.id;
  if (!pageId) return console.log("Invalid Confluence payload");

  try {
    console.log("Calling Confluence enrichment API");

    const response = await axios.post(
      "http://localhost:5001/enrich/confluence",
      { pageId }
    );

    const enriched = response.data.pageDetails;

    const content = enriched.content;
    const cleanText = cleanHTML(content);

    const fullData = {
      pageId: enriched.id,
      title: enriched.title,
      version: enriched.version,
      content: cleanText,
      summary: cleanText.slice(0, 200),
      space: payload.page?.spaceKey,
      url: payload.page?.self,
      updatedBy: {
        accountId: payload.userAccountId,
        displayName: payload.userDisplayName,
      },
      eventType: payload.eventType,
      change: {
        versionBefore: enriched.version - 1,
        versionAfter: enriched.version
      }
    };

    console.log("CONFLUENCE FULL DATA:", JSON.stringify(fullData, null, 2));
    
    if (!hasChanged(pageId, fullData)) {
      console.log("Confluence no change");
      return;
    }

    channel.sendToQueue(
      "normalization_queue",
      Buffer.from(JSON.stringify({ ...data, fullData })),
      { persistent: true }
    );

    console.log("Confluence sent to Normalization_Queue");

  } catch (err) {
    console.error(
      "Confluence enrichment error:",
      err.response?.data || err.message
    );
  }
};