function Message({ message, onCiteClick }) {
  const renderContent = (text) => {
    if (!text) return null;
    if (message.role === "user") return text;
    
    const parts = text.split(/(\[\d+\])/g);
    
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const index = parseInt(match[1], 10) - 1;
        const source = message.sources && message.sources[index];
        if (source && onCiteClick) {
          return (
            <span
              key={i}
              onClick={() => onCiteClick(source)}
              style={{ color: '#007bff', cursor: 'pointer', textDecoration: 'underline', fontWeight: 'bold' }}
              title={`View Source ${index + 1}`}
            >
              {part}
            </span>
          );
        }
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div
      className={`message ${
        message.role === "user"
          ? "user"
          : "assistant"
      }`}
      style={{ whiteSpace: "pre-wrap", lineHeight: "1.5" }}
    >
      {renderContent(message.content)}
    </div>
  );
}

export default Message;