import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import TypingText from "./components/TypingText";
import jsPDF from "jspdf";


function App() {
  const [pdf, setPdf] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [pdfs, setPdfs] = useState([]);
  const [pdfCount, setPdfCount] = useState(0);
  const chatEndRef = useRef(null);
  const [expandedSource, setExpandedSource] =
  useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [showSidebar, setShowSidebar] = useState(false);


  
  useEffect(() => {
  loadStatus();
}, []);

useEffect(() => {
  chatEndRef.current?.scrollIntoView({
    behavior: "smooth",
  });
}, [messages]);

  const loadStatus = async () => {
  try {

    const response = await axios.get(
      "http://127.0.0.1:8000/status"
    );

    setPdfs(response.data.uploaded_pdfs);
    setPdfCount(response.data.total_pdfs);

  } catch (error) {

    console.log(error);

  }
};

  // =========================
  // Upload PDF
  // =========================

  const uploadPDF = async () => {
    if (!pdf) {
      alert("Please choose a PDF");
      return;
    }

    const formData = new FormData();
    formData.append("file", pdf);

    try {
      setLoading(true);

      const response = await axios.post(
        "https://production-rag-system-production-004f.up.railway.app/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setPdfs(response.data.pdfs);
      setPdfCount(response.data.total_pdfs);

      alert("PDF Uploaded Successfully");
    } catch (error) {
      console.log(error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // Ask Question
  // =========================

  const askQuestion = async () => {
    if (!question.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      text: question,
      time: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      setLoading(true);

      const response = await axios.post(
        "https://production-rag-system-production-004f.up.railway.app/ask",
        {
          question: question,
        }
      );

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        text: response.data.answer,
        sources: response.data.documents,
        scores: response.data.scores,
        responseTime:
          response.data.response_time,
        time: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, botMessage]);

      setQuestion("");
    } catch (error) {
      console.log(error);

      const errorMessage = {
        type: "bot",
        text: "Error getting response",
        time: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // Clear Database
  // =========================

  const clearDatabase = async () => {
    try {
      await axios.post(
        "https://production-rag-system-production-004f.up.railway.app/clear"
      );

      setMessages([]);
      setPdfs([]);
      setPdfCount(0);

      alert("Database Cleared");
    } catch (error) {
      console.log(error);
    }
  };

  const exportChat = () => {

        if (messages.length === 0) {
          alert("No chat to export");
          return;
        }

        let content = "";

        messages.forEach((msg) => {

          content +=
            `${msg.type.toUpperCase()}\n`;

          content +=
            `${msg.text}\n\n`;

          content +=
            "---------------------------------\n\n";
        });

        const blob = new Blob(
          [content],
          {
            type: "text/plain"
          }
        );

        const url =
          window.URL.createObjectURL(blob);

        const link =
          document.createElement("a");

        link.href = url;

        link.download =
          "chat_history.txt";

        link.click();

        window.URL.revokeObjectURL(url);
      };

  const exportPDF = () => {

  if (messages.length === 0) {
    alert("No chat to export");
    return;
  }

  const doc = new jsPDF();

  let y = 20;

  doc.setFontSize(18);
  doc.text("RAG Chat Report", 20, y);

  y += 15;

  messages.forEach((msg) => {

    const role =
      msg.type.toUpperCase();

    const text =
      `${role}: ${msg.text}`;

    const lines =
      doc.splitTextToSize(
        text,
        170
      );

    doc.text(lines, 20, y);

    y += lines.length * 8;

    y += 5;

    if (y > 260) {
      doc.addPage();
      y = 20;
    }

  });

  doc.save("chat_report.pdf");
};



 // =========================
  // Enter Key
  // =========================

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      askQuestion();
    }
  };

return (
  <div className={darkMode ? "container dark" : "container"}>

    {/* Mobile Overlay */}
    {showSidebar && (
      <div
        className="sidebar-overlay"
        onClick={() => setShowSidebar(false)}
      />
    )}

    {/* Sidebar */}
    <div
      className={`sidebar ${
        showSidebar ? "sidebar-open" : ""
      }`}
    >

      {/* Close Button */}
      <button
        className="close-sidebar"
        onClick={() => setShowSidebar(false)}
      >
        ✕
      </button>

      <div>

        <div className="logo-section">
          
          <h2>RAG Assistant</h2>
        </div>

        <div className="sidebar-stats">

          <div className="mini-stat">
            <span>📄 Docs</span>
            <strong>{pdfCount}</strong>
          </div>

          <div className="mini-stat">
            <span>💬 Messages</span>
            <strong>{messages.length}</strong>
          </div>

        </div>

        {/* KEEP ALL YOUR EXISTING SIDEBAR CODE BELOW */}
        

        <h3 className="pdf-title">
          📚 Uploaded PDFs
        </h3>

        <div className="pdf-list">
          {pdfs.map((pdf, index) => (
            <div key={index} className="pdf-card">
              <div className="pdf-name">📄 {pdf}</div>
            </div>
          ))}
        </div>

        <div className="upload-section">

          <div className="upload-box">

              <p>📄 Drag & Drop PDF</p>

              <input
                    className="file-input"
                    type="file"
                    accept=".pdf"
                    onChange={(e) =>
                      setPdf(e.target.files[0])
                    }
                  />

                </div>

          <button
            className="upload-btn"
            onClick={uploadPDF}
            disabled={loading}
          >
            {loading
              ? "Uploading..."
              : "📤 Upload PDF"}
          </button>

        </div>

      </div>

      <div className="sidebar-bottom">

        <button
          className="export-btn"
          onClick={exportChat}
        >
          📥 Export Chat
        </button>

        <button
          className="pdf-btn"
          onClick={exportPDF}
        >
          📄 Export PDF
        </button>

        <button
          className="theme-btn"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>

        <button
          className="clear-btn"
          onClick={clearDatabase}
        >
          🗑 Clear Database
        </button>

      </div>

    </div>

    {/* Main Content */}

    <div className="main-content">
      <button
        className="mobile-menu-btn"
        onClick={() => setShowSidebar(true)}
      >
        ☰
      </button>

      <div className="header">
        <h1> Production RAG System</h1>

        <p>
          Upload PDFs and ask intelligent questions
        </p>
      </div>

      <div className="stats">

        <div className="stat-card">
          <h4>Documents Loaded</h4>
          <p>{pdfCount}</p>
        </div>

        <div className="stat-card">
          <h4>Messages</h4>
          <p>{messages.length}</p>
        </div>

        <div className="stat-card">
          <h4>Status</h4>
          <p>
            {pdfCount > 0
              ? "Ready"
              : "No PDFs"}
          </p>
        </div>

      </div>

      {/* Chat */}

      <div className="chat-box">

        {messages.length === 0 && !loading && (

          <div className="welcome-screen">

            <h2>
               Production RAG System
            </h2>

            <p>
              Upload PDFs and ask intelligent questions.
            </p>

            <div className="welcome-features">

              <div className="feature-card">
                📄 Multiple PDF Support
              </div>

              <div className="feature-card">
                🔍 Semantic Search
              </div>

              <div className="feature-card">
                🧠 AI Powered Answers
              </div>

              <div className="feature-card">
                ⚡ Fast Retrieval
              </div>

            </div>

          </div>

        )}

        {messages.map((msg, index) => (

          <div
            key={msg.id}
            className={
              msg.type === "user"
                ? "message user"
                : "message bot"
            }
          >

            {
              msg.type === "bot"
                ? <TypingText text={msg.text} />
                : <p>{msg.text}</p>
            }

            <div className="message-time">
              {msg.time}
            </div>

            {msg.responseTime && (
              <div className="response-time">
                ⚡ {msg.responseTime}s
              </div>
            )}

            {msg.sources && (

              <div className="sources">

                <button
                  className="source-toggle"
                  onClick={() =>
                    setExpandedSource(
                      expandedSource === index
                        ? null
                        : index
                    )
                  }
                >
                  📚 Sources ({msg.sources.length})
                </button>

                {expandedSource === index &&
                  msg.sources.map((source, i) => (

                    <div
                      key={i}
                      className="source-box"
                    >

                      <div>
                        <strong>Score:</strong>{" "}
                        {msg.scores?.[i]?.toFixed(3)}
                      </div>

                      <hr />

                      {
                        typeof source === "object"
                          ? source.content
                          : source
                      }

                    </div>

                  ))
                }

              </div>

            )}

          </div>

        ))}

        {loading && (
          <div className="message bot">
            ⏳ AI is thinking...
          </div>
        )}

        <div ref={chatEndRef}></div>

      </div>

      {/* Input */}

      <div className="input-section">

        <input
          type="text"
          placeholder="Ask question from PDF..."
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          onKeyDown={handleKeyPress}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
        >
          {loading
            ? "Thinking..."
            : "Send"}
        </button>

      </div>

    </div>

  </div>
);
}

export default App;
