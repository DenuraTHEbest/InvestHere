const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// 1) CONNECT TO YOUR MONGO DB
// Include the database name "IndividualDB2" in the connection string.
mongoose
  .connect(
    "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/IndividualDB2?retryWrites=true&w=majority&appName=Cluster01"
  )
  .then(() => console.log("✅ Connected to MongoDB"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// 2) DEFINE A SCHEMA FOR YOUR COLLECTION
// This schema expects fields like Company_Name, Date, Actual_Final and dynamic predicted fields.
// Using { strict: false } allows additional fields such as Predicted_Day_1 ... Predicted_Day_20.
const companyPredictionSchema = new mongoose.Schema(
  {
    Company_Name: String,
    Date: Date,
    Actual_Final: Number,
    // You can optionally define explicit predicted fields:
    Predicted_Day_1: Number,
    Predicted_Day_2: Number,
    // ...
    Predicted_Day_20: Number,
  },
  { strict: false }
);

// 3) CREATE A MODEL FOR THAT COLLECTION
// The third argument must match your actual collection name exactly.
const CompanyPrediction = mongoose.model(
  "CompanyPrediction",
  companyPredictionSchema,
  "Compnay_Predictions3"
);

// 4) DEFINE ROUTES
// Frontend will fetch data from "http://localhost:5002/api/predictions"
app.get("/api/predictions", async (req, res) => {
  try {
    const allDocs = await CompanyPrediction.find();
    console.log("Documents fetched:", allDocs.length);
    res.json(allDocs);
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).json({ message: "Error fetching data" });
  }
});

// OPTIONAL: Sample insert route to add sample documents.
app.post("/api/insert-sample", async (req, res) => {
  const sampleData = [
    {
      Company_Name: "SAMPLE CO",
      Date: new Date("2023-10-01"),
      Actual_Final: 100,
      Predicted_Day_1: 105,
      // ...
    },
    {
      Company_Name: "ANOTHER SAMPLE CO",
      Date: new Date("2023-10-02"),
      Actual_Final: 200,
      Predicted_Day_1: 195,
      // ...
    },
  ];
  try {
    await CompanyPrediction.insertMany(sampleData);
    res.json({ message: "Sample data inserted successfully" });
  } catch (error) {
    console.error("Error inserting sample data:", error);
    res.status(500).json({ message: "Error inserting sample data" });
  }
});

// 5) START THE SERVER
const PORT = 5002;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
