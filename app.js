const express = require("express");
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Calculator endpoints
app.post("/api/add", (req, res) => {
  const { a, b } = req.body;
  if (typeof a !== "number" || typeof b !== "number") {
    return res.status(400).json({ error: "Invalid input" });
  }
  res.json({ result: a + b });
});

app.post("/api/subtract", (req, res) => {
  const { a, b } = req.body;
  if (typeof a !== "number" || typeof b !== "number") {
    return res.status(400).json({ error: "Invalid input" });
  }
  res.json({ result: a - b });
});

app.post("/api/multiply", (req, res) => {
  const { a, b } = req.body;
  if (typeof a !== "number" || typeof b !== "number") {
    return res.status(400).json({ error: "Invalid input" });
  }
  res.json({ result: a * b });
});

app.post("/api/divide", (req, res) => {
  const { a, b } = req.body;
  if (typeof a !== "number" || typeof b !== "number") {
    return res.status(400).json({ error: "Invalid input" });
  }
  if (b === 0) {
    return res.status(400).json({ error: "Division by zero" });
  }
  res.json({ result: a / b });
});

app.get("/health", (req, res) => {
  res.json({ status: "healthy" });
});

app.listen(PORT, () => {
  console.log(`Calculator app running on port ${PORT}`);
});

module.exports = app;
