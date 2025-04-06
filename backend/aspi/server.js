const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect("mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/aspi_database?retryWrites=true&w=majority")
  .then(() => console.log("✅ Connected to MongoDB"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// Define a schema for ASPI predictions
const aspiPredictionSchema = new mongoose.Schema({
  Date: Date,
  Predicted_Day_1: Number,
  Actual_Day_1: Number,
});

const ASPIPrediction = mongoose.model("aspi_data", aspiPredictionSchema, "aspi_data");

// API to fetch ASPI data for the chart
app.get("/", async (req, res) => {
  try {
    const data = await ASPIPrediction.find().sort({ Date: 1 });

    // Process data to separate actual and predicted values
    const processedData = data.map((item) => ({
      date: item.Date.toISOString().split("T")[0], // Format date as YYYY-MM-DD
      actual: item.Actual_Day_1 || null, // Use null if actual value is missing
      predicted: item.Predicted_Day_1 || null, // Use null if predicted value is missing
    }));

    res.json(processedData);
  } catch (error) {
    res.status(500).json({ message: "Error fetching data" });
  }
});

// Route to insert sample data
app.post("/insert-sample-data", async (req, res) => {
  const sampleData = [
    {
      Date: new Date("2023-10-01"),
      Predicted_Day_1: 1200,
      Actual_Day_1: 1210,
    },
    {
      Date: new Date("2023-10-02"),
      Predicted_Day_1: 1220,
      Actual_Day_1: 1215,
    },
  ];

  try {
    await ASPIPrediction.insertMany(sampleData);
    res.json({ message: "Sample data inserted successfully" });
  } catch (error) {
    res.status(500).json({ message: "Error inserting sample data" });
  }
});

// Start the server
app.listen(5050, () => console.log("Server running on http://localhost:5050"));