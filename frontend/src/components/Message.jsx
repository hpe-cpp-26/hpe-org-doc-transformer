import { useState } from "react";

function Message({ message, setSelectedDoc }) {
  const [showSources, setShowSources] = useState(false);
  const sources = message.sources || [];

  return (
    <div
      className={`message ${
        message.role === "user" ? "user" : "assistant"
      }`}
    >
      {/* MESSAGE CONTENT */}
      <div className="message-content">{message.content}</div>

      {/* SOURCES BUTTON (only for assistant + sources exist) */}
      {message.role === "assistant" && sources.length > 0 && (
        <button
          onClick={() => setShowSources(!showSources)}
          style={{
            marginTop: "6px",
            fontSize: "12px",
            background: "transparent",
            border: "none",
            cursor: "pointer",
            color: "#666",
          }}
        >
          {showSources
            ? "Hide sources ▲"
            : `Sources (${sources.length}) ▼`}
        </button>
      )}

      {/* SOURCES PANEL */}
      {showSources && sources.length > 0 && (
        <div
          style={{
            marginTop: "10px",
            paddingLeft: "10px",
            borderLeft: "3px solid #ddd",
          }}
        >
          {sources.map((c, index) => (
            <div
              key={index}
              onClick={() =>
                setSelectedDoc?.({
                  title: c.doc_id,
                  source: c.doc_id,
                  path: c.doc_path,
                  url: c.url,
                  content: c.doc_path,
                })
              }
              style={{
                marginBottom: "10px",
                padding: "8px",
                background: "#f9f9f9",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              <div style={{ fontWeight: "600" }}>
                [{index + 1}] {c.doc_id}
              </div>

              {c.doc_path && (
                <div style={{ fontSize: "12px", color: "#555" }}>
                  {c.doc_path}
                </div>
              )}

              {c.url && (
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: "12px" }}
                >
                  {c.url}
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Message;