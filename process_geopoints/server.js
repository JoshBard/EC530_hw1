const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

// Ensure required directories exist
const uploadDirs = ["uploads/your_points", "uploads/option_points"];
uploadDirs.forEach((dir) => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Multer storage config
const storage = (uploadPath) =>
  multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadPath),
    filename: (req, file, cb) => cb(null, file.originalname),
  });

const uploadYourPoints = multer({ storage: storage("uploads/your_points") });
const uploadOptionPoints = multer({ storage: storage("uploads/option_points") });

// Function to enforce single file per directory
const enforceSingleFile = (directory) => {
  const files = fs.readdirSync(directory);
  if (files.length > 1) {
    fs.unlinkSync(path.join(directory, files[0])); // Remove the oldest file
  }
};

// Function to run the Python parser after upload
const runCsvParser = (filePath) => {
  console.log(`🔄 Running parser on: ${filePath}`);
  exec(`python3 processing/csv_parser.py "${filePath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`❌ Error running parser: ${error.message}`);
      return;
    }
    console.log(`✅ Parser Output:\n${stdout || stderr}`);
  });
};

// Upload handlers with auto-parser
app.post("/upload/your_points", uploadYourPoints.single("csvFile"), (req, res) => {
  if (!req.file) return res.status(400).json({ message: "No file uploaded" });

  enforceSingleFile("uploads/your_points");
  const filePath = path.join(__dirname, "uploads/your_points", req.file.filename);
  runCsvParser(filePath);

  res.json({ message: "Your Points uploaded and processed successfully", file: req.file });
});

app.post("/upload/option_points", uploadOptionPoints.single("csvFile"), (req, res) => {
  if (!req.file) return res.status(400).json({ message: "No file uploaded" });

  enforceSingleFile("uploads/option_points");
  const filePath = path.join(__dirname, "uploads/option_points", req.file.filename);
  runCsvParser(filePath);

  res.json({ message: "Option Points uploaded and processed successfully", file: req.file });
});

// Manual CSV Upload handlers
app.post("/uploadManual/:type", (req, res) => {
  const { csvData } = req.body;
  const type = req.params.type;
  const directory = `uploads/${type}`;

  if (!csvData) return res.status(400).json({ message: "No CSV data provided" });

  const filename = `manual_${Date.now()}.csv`;
  const filePath = path.join(directory, filename);
  fs.writeFileSync(filePath, csvData);

  enforceSingleFile(directory);
  runCsvParser(filePath);

  res.json({ message: `${type} CSV data saved and processed successfully`, file: { filename } });
});

// Get uploaded files
app.get("/uploads", (req, res) => {
  const yourPoints = fs.readdirSync("uploads/your_points").map((file) => ({ filename: file }));
  const optionPoints = fs.readdirSync("uploads/option_points").map((file) => ({ filename: file }));

  res.json({ your_points: yourPoints[0] || null, option_points: optionPoints[0] || null });
});

// Clear specific uploads
app.delete("/clearUploads/:type", (req, res) => {
  const type = req.params.type;
  const directory = `uploads/${type}`;

  fs.readdirSync(directory).forEach((file) => fs.unlinkSync(path.join(directory, file)));
  res.json({ message: `Cleared all files in ${type}` });
});

app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
