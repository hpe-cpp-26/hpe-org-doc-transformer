const Diff = require("diff");

function extractAddedContent (
    oldContent,
    newContent
){

    const changes = Diff.diffLines(
        oldContent,
        newContent
    );

    let addedLines = [];

    changes.forEach((part) => {
        
        if(part.added) {
            addedLines.push(
                part.value
            );
        }
    });

    return addedLines
    .join("\n")
    .trim();
}

module.exports = {
    extractAddedContent,
};