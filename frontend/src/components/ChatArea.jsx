import { useState, useRef, useEffect } from "react";
import Message from "./Message";
import { searchDocuments } from "../services/api";

const formatTitle = (doc_id) => {
  if (!doc_id) return "Untitled";
  return doc_id
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ")
    .replace(/\s(Chunk|Vec|Id)\s?\d*/gi, "")
    .trim();
};

function ChatArea({ setSelectedDoc }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userQuery = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setLoading(true);

    try {
      const data = await searchDocuments(userQuery);

      const normalizedSources = (data.sources || []).slice(0, 3).map((s) => ({
        title: formatTitle(s.doc_id),
        path: s.doc_path || "",
        content: s.chunk_text || "No content available.",
        url: s.url || null,
        similarity: s.similarity ?? null,
      }));

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No answer returned.",
          confidence: data.confidence_score ?? null,
          sources: normalizedSources,
        },
      ]);
    } catch (err) {
      console.error("Search failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Ask a question about your project documentation.</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <Message key={index} message={msg} onCiteClick={setSelectedDoc} />
        ))}
        {loading && (
          <div className="loading-indicator">
            <div className="loading-dot" />
            <div className="loading-dot" />
            <div className="loading-dot" />
            <span>Searching documentation…</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input">
          <input
            value={input}
            placeholder="Search documentation…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading}>
            Search
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatArea;
