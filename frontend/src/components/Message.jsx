import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Message({ message, onCiteClick }) {
  const [showSources, setShowSources] = useState(false);
  const sources = message.sources || [];

  const renderMarkdown = (text) => {
    if (!text) return null;

    const processedText = text.replace(/\[(\d+)\](?!\()/g, "[$1](#cite-$1)");

    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children, ...props }) => {
            if (href && href.startsWith("#cite-")) {
              const index = parseInt(href.replace("#cite-", ""), 10) - 1;
              const source = message.sources && message.sources[index];
              if (source && onCiteClick) {
                return (
                  <span
                    className="cite-badge"
                    onClick={(e) => {
                      e.preventDefault();
                      onCiteClick(source);
                    }}
                    title={`View Source ${index + 1}`}
                  >
                    {children}
                  </span>
                );
              }
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
                {children}
              </a>
            );
          },
        }}
      >
        {processedText}
      </ReactMarkdown>
    );
  };

  return (
    <div className={`message ${message.role === "user" ? "user" : "assistant"}`}>
      {message.role === "user" ? (
        <div style={{ whiteSpace: "pre-wrap" }}>{message.content}</div>
      ) : (
        <div>
          <div className="markdown-body">
            {renderMarkdown(message.content)}
          </div>

          {message.confidence != null && (
            <div className="confidence-tag">
              Confidence: {message.confidence}%
            </div>
          )}
        </div>
      )}

      {message.role === "assistant" && sources.length > 0 && (
        <button
          className="sources-toggle"
          onClick={() => setShowSources(!showSources)}
        >
          {showSources ? "Hide sources" : `${sources.length} sources`}
        </button>
      )}

      {showSources && sources.length > 0 && (
        <div className="sources-panel">
          {sources.map((s, index) => (
            <div
              key={index}
              className="source-card"
              onClick={() => onCiteClick?.(s)}
            >
              <div className="source-card-header">
                <div className="source-card-title">
                  <span className="source-icon">📄</span>
                  {s.title || "Untitled"}
                </div>
                {s.similarity != null && (
                  <span className="source-card-similarity">
                    {Math.round(s.similarity * 100)}%
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Message;
