const fs = require('fs');
const code = `function extractReadmeData(readme){
    if(!readme || !readme.trim()){
        return { description: "", features: [] };
    }
    if(readme.includes("#FILE:")){
        const features = readme.split("\\n").map(l=>l.trim()).filter(l=>l.startsWith("-")||l.startsWith("*")).map(l=>l.replace(/^[-*]\\s*/,""));
        return { description: readme.trim(), features };
    }
    let description = readme.trim();
    let features = readme.split("\\n").map(l=>l.trim()).filter(l=>l.startsWith("-")||l.startsWith("*")).map(l=>l.replace(/^[-*]\\s*/,""));
    return { description, features };
}
module.exports = {extractReadmeData};`;
fs.writeFileSync('consumer/utils/readmeParser.js', code);
console.log('Done');