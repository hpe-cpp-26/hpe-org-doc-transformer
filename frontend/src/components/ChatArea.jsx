import { useState } from "react";
import Message from "./Message";
import SearchResultCard from "./SearchResultCard";
import { searchDocuments } from "../services/api";

function ChatArea({ setSelectedDoc }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Ask me anything about your documents.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userQuery = input;
    setInput("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuery },
    ]);

    setLoading(true);

    try {
      const data = await searchDocuments(userQuery);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.results.length
            ? `Found ${data.results.length} relevant chunk(s).`
            : "No documents found for your query.",
          sources: data.results ?? [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          sources: [],
        },
      ]);
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index}>
            <Message message={msg} />

            {msg.sources &&
              msg.sources.map((source, i) => (
                <SearchResultCard
                  key={i}
                  data={{
                    title: `Document ${source.doc_id}`,
                    source: `Similarity: ${(source.similarity * 100).toFixed(1)}%`,
                    similarity: source.similarity,
                  }}
                  onClick={() =>
                    setSelectedDoc({
                      title: `Document ${source.doc_id}`,
                      source: `doc_id: ${source.doc_id}`,
                      path: `doc_id: ${source.doc_id}`,
                      content: source.chunk_text,
                    })
                  }
                />
              ))}
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <p>Searching documents...</p>
          </div>
        )}
      </div>

      <div className="chat-input">
        <input
          value={input}
          placeholder="Ask a question..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />

        <button onClick={sendMessage} disabled={loading}>
          {loading ? "Searching..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatArea;