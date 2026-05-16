function extractReadmeData(readme){
    if(!readme || !readme.trim())
    {
        return {
            description : "",
            features : [],
        };
    }

    let description = "";
    let features = [];

    //first the usual structured extraction

    const descMatch = readme.match(
        /#.*\n([\s\S]*?)(\n##|\n$)/
    );

    //checks if the regex is matched and returns the first captured content
    if(descMatch && descMatch[1]){
        description = descMatch[1].trim();
    }

    const featuresMatch = readme.match(
           /## Features([\s\S]*?)(\n##|\n$)/i
    );

    if(featuresMatch && featuresMatch[1]){
        features = featuresMatch[1]
        .split("\n")
        .map(line => 
            line.replace(/[-*]/g, "").trim()
        )
        .filter(Boolean);
    }

    //updated fallback logic if no description and features title is found

    //if no description then replaces the description with the first 5 lines of the readme
    if(!description)
    {
        const cleaned = readme
        .replace(/^#+\s.*$/gm, "")
        .trim();

        description = cleaned 
        .split("\n")
        .map(line => line.trim()) 
        .filter(Boolean)
        .slice(0 , 5)
        .join(" ");
    }

    //if no features then looks for lines starting with either '-' or '*'
    if(features.length === 0)
    {
        features = readme 
        .split("\n")
        .map(line => line.trim())
        .filter(line => 
            line.startsWith("-") || line.startsWith("*")
        )
        .map(line => 
            line.replace(/^[-*]\s*/, "")
        );
    }

    return {
        description ,
        features,
    };
}

module.exports = {extractReadmeData};