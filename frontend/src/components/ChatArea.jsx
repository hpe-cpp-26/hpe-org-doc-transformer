import { useState } from "react";
import Message from "./Message";
import { searchDocuments } from "../services/api";
import Sidebar from "./Sidebar";

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
      {
        role: "user",
        content: userQuery,
      },
      {
        role: "user",
        content: userQuery,
      },
    ]);

    setLoading(true);

    try {
      const data = await searchDocuments(userQuery);

      const answerWithConfidence = `
${data.answer || "No answer returned."}

Confidence Score: ${data.confidence_score ?? "N/A"}%
      `.trim();

      const answerWithConfidence = `
${data.answer || "No answer returned."}

Confidence Score: ${data.confidence_score ?? "N/A"}%
      `.trim();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: answerWithConfidence,
          sources: (data.sources || []).slice(0, 3),
        },
      ]);
    } catch (err) {
      console.error("Search failed:", err);

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
    if (e.key === "Enter") {
      sendMessage();
    }
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index}>
            <Message message={msg} setSelectedDoc={setSelectedDoc} />
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