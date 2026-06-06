import { useState } from "react";
import API from "../api";

function UploadPDF() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await API.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert(response.data.message);
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>
        Upload PDF
      </button>
    </div>
  );
}

export default UploadPDF;