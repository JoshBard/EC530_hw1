import React, { useState, useEffect } from "react";

function App() {
  const [yourFile, setYourFile] = useState(null);
  const [optionFile, setOptionFile] = useState(null);
  const [yourCSV, setYourCSV] = useState("");
  const [optionCSV, setOptionCSV] = useState("");
  const [downloadUrl, setDownloadUrl] = useState(null);

  useEffect(() => {
    fetch("http://localhost:4000/uploads")
      .then((res) => res.json())
      .then((data) => {
        setYourFile(data.your_points);
        setOptionFile(data.option_points);
      });
  }, []);

  const handleFileUpload = async (file, type) => {
    const formData = new FormData();
    formData.append("csvFile", file);

    try {
      const response = await fetch(`http://localhost:4000/upload/${type}`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      alert(result.message);
      if (type === "your_points") setYourFile(result.file);
      else setOptionFile(result.file);
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed.");
    }
  };

  const handleManualUpload = async (csvData, type) => {
    if (!csvData.trim()) {
      alert("Enter CSV data before uploading.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:4000/uploadManual/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ csvData }),
      });

      const result = await response.json();
      alert(result.message);
      if (type === "your_points") setYourFile(result.file);
      else setOptionFile(result.file);
    } catch (error) {
      console.error("Manual upload error:", error);
      alert("Upload failed.");
    }
  };

  const clearUploads = async (type) => {
    try {
      const response = await fetch(`http://localhost:4000/clearUploads/${type}`, { method: "DELETE" });
      const result = await response.json();
      alert(result.message);
      if (type === "your_points") setYourFile(null);
      else setOptionFile(null);
    } catch (error) {
      console.error("Clear error:", error);
      alert("Failed to clear.");
    }
  };

  const handleMatchPoints = async () => {
    try {
      const response = await fetch("http://localhost:4000/matchPoints", { method: "POST" });
      const result = await response.json();
      alert(result.message);
      setDownloadUrl(result.downloadUrl);
    } catch (error) {
      console.error("Error matching points:", error);
      alert("Failed to process point matching.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>CSV Upload System</h1>

      {/* Your Points Upload */}
      <h2>Upload Your Points</h2>
      <input type="file" accept=".csv" onChange={(e) => handleFileUpload(e.target.files[0], "your_points")} />
      <h3>Or Enter CSV Manually</h3>
      <textarea
        rows="5"
        cols="50"
        placeholder="Type CSV content for Your Points..."
        value={yourCSV}
        onChange={(e) => setYourCSV(e.target.value)}
      />
      <br />
      <button onClick={() => handleManualUpload(yourCSV, "your_points")}>Upload Your CSV</button>
      <p>Current file: {yourFile ? yourFile.filename : "None"}</p>
      <button onClick={() => clearUploads("your_points")} style={{ color: "red" }}>Clear Your Points</button>

      <hr />

      {/* Option Points Upload */}
      <h2>Upload Option Points</h2>
      <input type="file" accept=".csv" onChange={(e) => handleFileUpload(e.target.files[0], "option_points")} />
      <h3>Or Enter CSV Manually</h3>
      <textarea
        rows="5"
        cols="50"
        placeholder="Type CSV content for Option Points..."
        value={optionCSV}
        onChange={(e) => setOptionCSV(e.target.value)}
      />
      <br />
      <button onClick={() => handleManualUpload(optionCSV, "option_points")}>Upload Option CSV</button>
      <p>Current file: {optionFile ? optionFile.filename : "None"}</p>
      <button onClick={() => clearUploads("option_points")} style={{ color: "red" }}>Clear Option Points</button>

      <hr />

      {/* Match Points Button */}
      <h2>Match Points</h2>
      <button onClick={handleMatchPoints} style={{ backgroundColor: "blue", color: "white", padding: "10px 20px" }}>
        Match Points
      </button>

      {/* Download Matched CSV Button */}
      {downloadUrl && (
        <div style={{ marginTop: "20px" }}>
          <a href={downloadUrl} download>
            <button style={{ backgroundColor: "green", color: "white", padding: "10px 20px" }}>
              Download Matched CSV
            </button>
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
