const express = require("express");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const fs = require("fs");
const multer = require("multer");

const PROTO_PATH = "../protos/media.proto";
const packageDefinition = protoLoader.loadSync(PROTO_PATH);
const proto = grpc.loadPackageDefinition(packageDefinition).videoUpload;

const app = express();
app.use(express.static(__dirname));
const port = 3000;

// gRPC Client
const grpcClient = new proto.VideoUploadService(
  "localhost:50051",
  grpc.credentials.createInsecure()
);

// Multer setup for handling file uploads
const upload = multer({ dest: "temp/" });

app.post("/upload", upload.single("video"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  }

  const filePath = req.file.path;
  const chunkSize = 64 * 1024; // 64 KB per chunk
  const totalChunks = Math.ceil(req.file.size / chunkSize);
  let chunkIndex = 0;

  console.log(`📂 Uploading file: ${req.file.originalname}`);
  console.log(`📏 File size: ${req.file.size} bytes`);
  console.log(`🔢 Total Chunks: ${totalChunks}`);

  const stream = grpcClient.uploadVideo((err, response) => {
    if (err) {
      console.error("🚨 gRPC Upload Error:", err);
      return res.status(500).json({ error: "gRPC Upload Failed" });
    }
    console.log("Response from gRPC server:", response);
    res.json({ message: "✅ Upload successful", response });
  });

  const fileStream = fs.createReadStream(filePath, {
    highWaterMark: chunkSize
  });

  let totalSent = 0;
  fileStream.on("data", chunk => {
    const isLastChunk = chunkIndex === totalChunks - 1;

    console.log(
      `📤 Sending chunk ${chunkIndex +
        1}/${totalChunks} (Size: ${chunk.length} bytes)`
    );
    console.log(`🔎 isLastChunk: ${isLastChunk}`);

    totalSent++;
    stream.write({ data: chunk, chunkIndex, isLastChunk });
    // stream.resume(); // Ensure the stream is actively flowing
    chunkIndex++;
    console.log(totalSent);

    if (isLastChunk) {
      // End the stream to notify the server that no more chunks will be sent
      console.log("Last chunk sent, closing stream.");
      stream.end(); // End the stream once the last chunk is sent
    }
  });

  fileStream.on("end", () => {
    console.log("✅ All chunks sent. Closing stream...");
    stream.end();
  });

  fileStream.on("error", err => {
    console.error("🚨 File streaming error:", err);
    res.status(500).json({ error: "File streaming error" });
  });
});

// Start Express Server
app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
