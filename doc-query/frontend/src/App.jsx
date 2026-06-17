import { useState } from "react";
import ChatArea from "./components/ChatArea";
import DocumentViewer from "./components/DocumentViewer";
import "./App.css";

function App() {
  const [selectedDoc, setSelectedDoc] = useState(null);

  return (
    <div className="app-container">
      <ChatArea setSelectedDoc={setSelectedDoc} />
      {selectedDoc && (
        <DocumentViewer
          document={selectedDoc}
          onClose={() => setSelectedDoc(null)}
        />
      )}
    </div>
  );
}

export default App;
