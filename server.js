const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

require("dotenv").config(); // Add this at the top
mongoose.connect(process.env.MONGO_URI); // Use the environment variable

// Connect to MongoDB
mongoose.connect("mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/aspi_database?retryWrites=true&w=majority");

// Define a schema for ASPI predictions
const aspiPredictionSchema = new mongoose.Schema({
  Date: Date,
  Predicted_Day_1: Number,
  Actual_Day_1: Number,
});

const ASPIPrediction = mongoose.model("ASPI_Prediction", aspiPredictionSchema);

// API to fetch ASPI data for the chart
app.get("/api/aspi/history", async (req, res) => {
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

// Start the server
app.listen(5000, () => console.log("Server running on http://localhost:5000"));