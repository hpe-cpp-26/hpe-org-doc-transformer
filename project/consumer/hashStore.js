const crypto = require("crypto");

const store = {};

const readmeContentStore = {};

function generateHash(data){
  return crypto
    .createHash("sha256")
    .update(JSON.stringify(data))
    .digest("hex");
}

function hashChanged(key , data){
  const newHash = generateHash(data);

  if(store[key] === newHash)
  {
      return false;
  }
    
    store[key] = newHash;
    return true;
}

    /* for new READM contents */

    function getReadmeContent(key) {
      return readmeContentStore[key] || "";
    }

    function updateReadmeContent(
      key,
      content
    ){
       readmeContentStore[key] = content;
    }

    function hashReadmeChanged(
      key,
      content
    ){
      const oldHash = generateHash(
        getReadmeContent(key)
      );

      const newHash = 
      generateHash(content);

      return oldHash !== newHash;
    }

    module.exports = {

      hashChanged,

      getReadmeContent,

      updateReadmeContent,

      hashReadmeChanged
    };
