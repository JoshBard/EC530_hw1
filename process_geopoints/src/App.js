import React, { useState } from "react";

function App() {
  const [files, setFiles] = useState([]);

  const handleFileChange = (event) => {
    setFiles(event.target.files); // Store selected files
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert("Please select at least one file!");
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append("csvFiles", file); // "csvFiles" matches backend field name
    });

    try {
      const response = await fetch("http://localhost:4000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      alert(result.message);
      console.log("Uploaded Files:", result.files);
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("File upload failed.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Upload CSV Files</h1>
      <input type="file" accept=".csv" multiple onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload
      </button>
    </div>
  );
}

export default App;
