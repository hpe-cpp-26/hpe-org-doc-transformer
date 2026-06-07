function Message({ message }) {
  return (
    <div
      className={`message ${
        message.role === "user"
          ? "user"
          : "assistant"
      }`}
    >
      {message.content}
    </div>
  );
}

export default Message;