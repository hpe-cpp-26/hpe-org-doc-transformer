const crypto = require("crypto");

const store = {};

function generateHash(data) {
  return crypto
    .createHash("sha256")
    .update(JSON.stringify(data))
    .digest("hex");
}

function hasChanged(key, data) {
  const newHash = generateHash(data);

  if (store[key] === newHash) {
    return false;
  }

  store[key] = newHash;
  return true;
}

module.exports = { hasChanged };