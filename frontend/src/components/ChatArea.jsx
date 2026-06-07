import { useState } from "react";
import Message from "./Message";
import SearchResultCard from "./SearchResultCard";

function ChatArea({ setSelectedDoc }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Ask me anything about your documents.",
    },
  ]);

  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: input,
      },
      {
        role: "assistant",
        content:
          "I found documents related to retries in the payment-system.",
        sources: [
          {
            title: "Payment Issue: Retry Logic",
            source: "Jira",
            similarity: 0.92,
          },
        ],
      },
    ]);

    setInput("");
  };

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index}>
            <Message message={msg} />

            {msg.sources &&
              msg.sources.map((source) => (
                <SearchResultCard
                  key={source.title}
                  data={source}
                  onClick={() =>
                    setSelectedDoc({
                      title: source.title,
                      source: source.source,
                      path:
                        "root/payment-system/jira/ticket1.md",
                      content:
                        "Ticket tracks retry backoff for transient gateway errors and alerts.",
                    })
                  }
                />
              ))}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          placeholder="Ask a question..."
          onChange={(e) => setInput(e.target.value)}
        />

        <button onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatArea;