import { useState, useRef, useEffect, useCallback } from "react";
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
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Keyboard shortcut: press "/" to focus the search input
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if (
        e.key === "/" &&
        !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName) &&
        !document.activeElement.isContentEditable
      ) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handleGlobalKeyDown);
    return () => document.removeEventListener("keydown", handleGlobalKeyDown);
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userQuery = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setLoading(true);

    try {
      const data = await searchDocuments(userQuery);

      const normalizedSources = (data.sources || []).map((s) => ({
        title: s.title || formatTitle(s.doc_id),
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
          query: userQuery,
          timestamp: new Date(),
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
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-area">
      {/* Header */}
      <div className="app-header">
        <div className="app-header-inner">
          <div className="app-logo">
            <span className="app-logo-icon" />
            <span className="app-logo-text">Documentation Search</span>
          </div>
        </div>
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
            </div>
            <span className="empty-state-heading">
              Search your documentation
            </span>
            <p>Ask a question and get answers from project docs.</p>
            <span className="keyboard-hint">
              Press <kbd>/</kbd> to focus search
            </span>
          </div>
        )}
        {messages.map((msg, index) => (
          <Message key={index} message={msg} onCiteClick={setSelectedDoc} />
        ))}
        {loading && (
          <div className="loading-skeleton" aria-label="Loading results">
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input">
          <input
            ref={inputRef}
            id="search-input"
            value={input}
            placeholder="Ask a question about your documentation…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            autoComplete="off"
          />
          <button
            className="chat-input-btn"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            Search
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatArea;
