import { useState, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const formatTime = (date) => {
  if (!date) return "";
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
};

const truncate = (text, maxLen = 140) => {
  if (!text || text.length <= maxLen) return text || "";
  return text.slice(0, maxLen).trimEnd() + "…";
};

/** Get confidence level for colour coding */
const confidenceLevel = (score) => {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
};

function Message({ message, onCiteClick }) {
  const [showSources, setShowSources] = useState(false);
  const [copied, setCopied] = useState(false);
  const sources = message.sources || [];

  const handleCopyAnswer = useCallback(() => {
    if (!message.content) return;
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [message.content]);

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
                    title={`View source ${index + 1}: ${source.title}`}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") onCiteClick(source);
                    }}
                  >
                    {children}
                  </span>
                );
              }
            }
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              >
                {children}
              </a>
            );
          },
          pre: ({ children, ...props }) => {
            const codeContent = extractCodeContent(children);
            return (
              <CodeBlock content={codeContent}>
                <pre {...props}>{children}</pre>
              </CodeBlock>
            );
          },
        }}
      >
        {processedText}
      </ReactMarkdown>
    );
  };

  /* ── User message ── */
  if (message.role === "user") {
    return (
      <div className="message user">
        <div className="message-user-bubble">{message.content}</div>
      </div>
    );
  }

  /* ── Assistant message — Report Card ── */
  return (
    <div className="message assistant">
      <div className="report-card">
        {/* ── Report Header ── */}
        <div className="report-header">
          <div className="report-header-left">
            <span className="report-label">Answer</span>
            {message.query && (
              <span className="report-query">
                — <em>{message.query}</em>
              </span>
            )}
          </div>
          <div className="report-header-right">
            {message.confidence != null && (
              <div className="confidence-meter">
                <span className="confidence-meter-label">Confidence</span>
                <div className="confidence-meter-bar">
                  <div
                    className={`confidence-meter-fill ${confidenceLevel(message.confidence)}`}
                    style={{ width: `${Math.min(message.confidence, 100)}%` }}
                  />
                </div>
                <span className="confidence-meter-value">
                  {message.confidence}%
                </span>
              </div>
            )}
            {message.timestamp && (
              <span className="report-timestamp">
                {formatTime(message.timestamp)}
              </span>
            )}
          </div>
        </div>

        {/* ── Report Body ── */}
        <div className="report-body">
          <div className="markdown-body">{renderMarkdown(message.content)}</div>
        </div>

        {/* ── Report Footer ── */}
        <div className="report-footer">
          <button
            className={`report-action-btn ${copied ? "copied" : ""}`}
            onClick={handleCopyAnswer}
            title="Copy answer to clipboard"
          >
            {copied ? (
              <>
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Copied
              </>
            ) : (
              <>
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
                Copy
              </>
            )}
          </button>

          {sources.length > 0 && (
            <button
              className="report-action-btn"
              onClick={() => setShowSources(!showSources)}
              aria-expanded={showSources}
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              {showSources
                ? "Hide sources"
                : `${sources.length} source${sources.length !== 1 ? "s" : ""}`}
            </button>
          )}
        </div>
      </div>

      {/* ── Expanded Sources ── */}
      {showSources && sources.length > 0 && (
        <div className="sources-section">
          <div className="sources-list" role="list">
            {sources.map((s, index) => (
              <div
                key={index}
                className="source-item"
                onClick={() => onCiteClick?.(s)}
                role="listitem"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter") onCiteClick?.(s);
                }}
              >
                <div className="source-item-left">
                  <span className="source-index">{index + 1}</span>
                  <div className="source-info">
                    <div className="source-title">{s.title || "Untitled"}</div>
                    {s.path && <div className="source-path">{s.path}</div>}
                    {s.content && (
                      <div className="source-snippet">
                        {truncate(s.content)}
                      </div>
                    )}
                  </div>
                </div>
                {s.similarity != null && (
                  <span className="source-similarity">
                    {Math.round(s.similarity * 100)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Helper: extract text content from a <pre> block's children ── */
function extractCodeContent(children) {
  if (!children) return "";
  if (typeof children === "string") return children;
  if (Array.isArray(children)) {
    return children.map(extractCodeContent).join("");
  }
  if (children.props) {
    return extractCodeContent(children.props.children);
  }
  return String(children);
}

/* ── CodeBlock: wrapper for <pre> with a copy button ── */
function CodeBlock({ content, children }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="code-block-wrapper">
      {children}
      <button
        className={`code-block-copy ${copied ? "copied" : ""}`}
        onClick={handleCopy}
        title="Copy code"
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}

export default Message;
