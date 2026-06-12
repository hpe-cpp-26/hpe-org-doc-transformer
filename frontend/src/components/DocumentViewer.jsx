import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function DocumentViewer({ document, onClose }) {
  return (
    <div className="doc-viewer">
      <div className="doc-viewer-header">
        <h2>{document.title}</h2>
        <span className="close-btn" onClick={onClose}>✕</span>
      </div>

      <div className="doc-viewer-meta">

        {document.url && (
          <div className="doc-meta-row">
            <span className="label">Link</span>
            <a href={document.url} target="_blank" rel="noreferrer">
              Open in repository →
            </a>
          </div>
        )}
      </div>

      <div className="doc-viewer-content">
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {document.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default DocumentViewer;