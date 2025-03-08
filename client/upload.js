const express = require("express");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const fs = require("fs");
const path = require("path");

const multer = require("multer");

const PROTO_PATH = "../protos/media.proto";
const packageDefinition = protoLoader.loadSync(PROTO_PATH);
const proto = grpc.loadPackageDefinition(packageDefinition).videoUpload;
const port = 3000;

const app = express();
const HLS_DIR = path.join(__dirname, "hls");

app.use(express.static(__dirname));
app.use("/hls", express.static(HLS_DIR));

// gRPC Client
const grpcClient = new proto.VideoUploadService(
  "localhost:50051",
  grpc.credentials.createInsecure()
);

// Multer setup for handling file uploads
let uploadProgress = 0;
const upload = multer({ dest: "temp/" });

app.post("/upload", upload.single("videoFile"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  }
  const videoTitle = req.body.videoTitle; // Get the video title from the form
  const filePath = req.file.path;
  const chunkSize = 64 * 1024; // 64 KB per chunk
  const totalChunks = Math.ceil(req.file.size / chunkSize);
  let firstChunk = 0;
  let isLastChunk = false;

  console.log(`Uploading file: ${req.file.originalname}`);
  console.log(`File size: ${req.file.size} bytes`);
  console.log(`VideoTitle${videoTitle}`);
  console.log(`Total Chunks: ${totalChunks}`);

  const stream = grpcClient.uploadVideo();

  stream.write({
    data: Buffer.from(`${videoTitle}-${totalChunks}`),
    firstChunk,
    isLastChunk
  });

  const fileStream = fs.createReadStream(filePath, {
    highWaterMark: chunkSize
  });

  let chunkIndex = 1;
  fileStream.on("data", chunk => {
    const isLastChunk = chunkIndex === totalChunks;

    console.log(
      `Sending chunk ${chunkIndex}/${totalChunks} (Size: ${chunk.length} bytes)`
    );
    stream.write({ data: chunk, chunkIndex, isLastChunk });
    chunkIndex++;
  });

  fileStream.on("end", () => {
    console.log("All chunks sent. Closing stream...");
    stream.end();
  });

  fileStream.on("error", err => {
    console.error("File streaming error:", err);
    res.status(500).json({ error: "File streaming error" });
  });

  stream.on("data", response => {
    if (response.status && response.status.progress) {
      uploadProgress = response.status.progress.toNumber();
      console.log(`📊 Updated progress: ${uploadProgress}%`);
    } else {
      console.warn("⚠️ Unexpected response structure:", response);
      // uploadProgress = response.status.progress.toNumber();
    }
  });

  stream.on("error", err => {
    console.log(err);
  });

  stream.on("end", () => {
    console.log("✅ Upload complete! Sending response...");
    res.json({ message: "Upload complete!" });
  });
});

app.get("/progress", (req, res) => {
  console.log("Start polling");
  res.json({ progress: uploadProgress });
  console.log(uploadProgress);
});

app.get("/video/new", (req, res) => {
  console.log("📡 Client requested video stream...");
  res.setHeader("Content-Type", "video/mp4");
  res.setHeader("Transfer-Encoding", "chunked");

  const call = grpcClient.StreamVideo({ filename: "new_h264.mp4" });

  // We need to track initialization segment separately
  let initSegmentSent = false;

  call.on("data", chunk => {
    // Handle initialization segment specially if needed
    if (chunk.chunkType === "init") {
      console.log(`🔹 Sending initialization segment`);
    } else {
      console.log(`🔹 Sending media chunk ${chunk.chunkIndex}`);
    }

    res.write(chunk.data);
  });

  call.on("end", () => {
    console.log("✅ Stream completed!");
    res.end();
  });

  call.on("error", err => {
    console.error("❌ gRPC error:", err);
    res.status(500).send("Error streaming video");
  });
});

// Start Express Server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
