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

app.post("/update-predictions", async (req, res) => {
  try {
    const updatedData = req.body; // Get the updated data from the request body

    // Step 1: Fetch the last 20 documents
    const last20Docs = await ASPIPrediction.find().sort({ Date: -1 }).limit(20); // Get the last 20 documents

    // Step 2: Update the predicted values for the last 20 documents
    for (let i = 0; i < last20Docs.length; i++) {
      if (i < updatedData.length) {
        last20Docs[i].Predicted_Day_1 = updatedData[i].predicted; // Update the predicted value
        await last20Docs[i].save(); // Save the updated document
      }
    }

    // Step 3: Update the actual value for the next day
    const nextDayData = updatedData.find((item) => item.actual !== null); // Find the next day's actual value
    if (nextDayData) {
      const nextDayDoc = await ASPIPrediction.findOne({ Date: new Date(nextDayData.date) });
      if (nextDayDoc) {
        // If the document for the next day exists, update its actual value
        nextDayDoc.Actual_Day_1 = nextDayData.actual;
        await nextDayDoc.save();
      } else {
        // If the document for the next day does not exist, create a new one
        await ASPIPrediction.create({
          Date: new Date(nextDayData.date),
          Predicted_Day_1: nextDayData.predicted || null,
          Actual_Day_1: nextDayData.actual,
        });
      }
    }

    res.json({ message: "Predictions and actual values updated successfully" });
  } catch (error) {
    res.status(500).json({ message: "Error updating predictions", error: error.message });
  }
});

// Start the server
app.listen(5050, () => console.log("Server running on http://localhost:5050"));
