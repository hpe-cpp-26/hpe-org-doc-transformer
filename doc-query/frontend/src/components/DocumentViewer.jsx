import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Get confidence level for colour coding */
const confidenceLevel = (score) => {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
};

function DocumentViewer({ document, onClose }) {
  const [isVisible, setIsVisible] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isHeaderCompact, setIsHeaderCompact] = useState(false);
  const [copied, setCopied] = useState(false);
  const contentRef = useRef(null);
  const panelRef = useRef(null);

  // Animate in on mount
  useEffect(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        setIsVisible(true);
      });
    });
  }, []);

  const handleClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(onClose, 280);
  }, [onClose]);

  // Close with Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        handleClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleClose]);

  // Reading progress and compact header
  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = el;
      const maxScroll = scrollHeight - clientHeight;
      if (maxScroll > 0) {
        setScrollProgress((scrollTop / maxScroll) * 100);
      }
      setIsHeaderCompact(scrollTop > 20);
    };

    el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el.removeEventListener("scroll", handleScroll);
  }, []);

  const handleOverlayClick = useCallback(
    (e) => {
      if (e.target === e.currentTarget) {
        handleClose();
      }
    },
    [handleClose],
  );

  const handleCopyContent = useCallback(() => {
    if (!document.content) return;
    navigator.clipboard.writeText(document.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [document.content]);

  const similarityPercent =
    document.similarity != null ? Math.round(document.similarity * 100) : null;

  const wordCount = document.content
    ? document.content.split(/\s+/).filter(Boolean).length
    : 0;
  const readingTime = Math.max(1, Math.ceil(wordCount / 200));

  return (
    <div
      className={`doc-viewer-overlay ${isVisible ? "visible" : ""}`}
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-label={`Source document: ${document.title}`}
    >
      <div
        ref={panelRef}
        className={`doc-viewer ${isVisible ? "open" : ""}`}
        role="document"
      >
        {/* Reading progress bar */}
        <div className="doc-viewer-progress">
          <div
            className="doc-viewer-progress-fill"
            style={{ width: `${scrollProgress}%` }}
          />
        </div>

        {/* Header */}
        <div
          className={`doc-viewer-header ${isHeaderCompact ? "compact" : ""}`}
        >
          <div className="doc-viewer-header-top">
            <div className="doc-viewer-header-left">
              <div className="doc-viewer-type-badge">
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
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
                <span>Source Document</span>
              </div>
              {similarityPercent != null && (
                <div
                  className={`doc-viewer-relevance-badge ${confidenceLevel(similarityPercent)}`}
                >
                  <span className="relevance-dot" />
                  <span>{similarityPercent}% match</span>
                </div>
              )}
            </div>
            <div className="doc-viewer-header-actions">
              <button
                className={`doc-viewer-action-btn ${copied ? "copied" : ""}`}
                onClick={handleCopyContent}
                title="Copy source content"
                aria-label="Copy source content"
              >
                {copied ? (
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
                ) : (
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
                )}
              </button>
              <button
                className="doc-viewer-close-btn"
                onClick={handleClose}
                title="Close panel (Esc)"
                aria-label="Close document viewer"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>
          Document Title
          <h2 className="doc-viewer-title" title={document.title}>
            {document.title || "Untitled Document"}
          </h2>
          {/* Meta row: path, reading time, link */}
          <div className="doc-viewer-meta-strip">
            {wordCount > 0 && (
              <div className="doc-meta-chip">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
                <span>{readingTime} min read</span>
              </div>
            )}
            {document.url && (
              <a
                href={document.url}
                target="_blank"
                rel="noreferrer"
                className="doc-meta-chip doc-meta-link"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
                <span>Open source</span>
              </a>
            )}
          </div>
        </div>

        {/* Divider */}
        <div className="doc-viewer-divider" />

        {/* Content */}
        <div className="doc-viewer-content" ref={contentRef}>
          <article className="doc-viewer-article">
            <div className="markdown-body doc-reader-typography">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {document.content}
              </ReactMarkdown>
            </div>
          </article>

          {/* Footer */}
          <div className="doc-viewer-footer">
            <div className="doc-viewer-footer-inner">
              <span className="doc-viewer-footer-hint">
                <kbd>Esc</kbd> to close
              </span>
              {wordCount > 0 && (
                <span className="doc-viewer-footer-stats">
                  {wordCount.toLocaleString()} words
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentViewer;
