import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

export const searchDocuments = async (query) => {
  const response = await api.post("/search", { query });
  return response.data;
};