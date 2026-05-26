function extractReadmeData(readme){
    if(!readme){
        return {};
    }

    const descMatch = readme.match(/#.*\n([\s\S]*?)(\n##|\n$)/);
    const description = descMatch ? descMatch[1].trim() : "";

    const featuresMatch = readme.match(/## Features([\s\S]*?)(\n##|\n$)/i);

    const features = featuresMatch 
    ? featuresMatch[1].split("\n")
    .map(line => line.replace(/[-*]/g, "").trim())
    .filter(Boolean)
    : [];

    return {description , features};

}
module.exports = {extractReadmeData};