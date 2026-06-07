export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2>🤖 RAG Chatbot</h2>

      <button>💬 New Chat</button>
      <button>📄 Documents</button>

      <div className="bottom">
        <button>🌙 Theme</button>
        <button className="clear-btn">
          🗑️ Clear Database
        </button>
      </div>
    </div>
  );
}