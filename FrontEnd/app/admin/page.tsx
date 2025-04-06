"use client";

import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export default function CSVUploadPage() {
  const [csvFile1, setCsvFile1] = useState<File | null>(null);
  const [csvFile2, setCsvFile2] = useState<File | null>(null);
  const [decimalValue, setDecimalValue] = useState<string>("");
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [aspiDate, setAspiDate] = useState<Date | undefined>(undefined);

  const handleFileChange = (setter: (file: File | null) => void) => (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setter(event.target.files[0]);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (setter: (file: File | null) => void) => (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      setter(event.dataTransfer.files[0]);
    }
  };

  const handleRemoveFile = (setter: (file: File | null) => void) => () => {
    setter(null);
  };

  const handleSubmit = async () => {
    console.log("CSV File 1:", csvFile1);
    console.log("CSV File 2:", csvFile2);
    console.log("Decimal Value:", decimalValue);
    console.log("ASPI Date:", aspiDate);

    const decimal = parseFloat(decimalValue);
    if (isNaN(decimal) || decimal < 10000 || decimal > 25000) {
      alert("Please enter a valid ASPI value between 10000 and 25000.");
      return;
    }
    if (!aspiDate) {
      alert("Please select a date.");
      return;
    }

    if (!csvFile1) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file1", csvFile1);
    formData.append("decimalValue", decimalValue); // Add decimalValue to the form data

    try {
      const response = await fetch("http://127.0.0.1:5050/process_news", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      console.log("Response:", data);
      console.log("Response Status:", response.status);

      if (response.status === 200 && data.status === "success") {
        console.log("File uploaded successfully:", data);
        alert(data.message || "File uploaded and processed successfully!");
        window.location.reload();
      } else {
        console.error("Failed to upload file:", data);
        alert(data.message || "Failed to process the file");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      alert(`Failed to upload the file: ${errorMessage}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex flex-col items-center justify-center p-6 text-white">
      <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-purple-500">
        Advanced Stock Market Predictions Admin Page
      </h1>

      <div className="w-full max-w-2xl bg-gray-900 rounded-lg p-8 shadow-lg border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6 text-gray-200">Upload Market Data</h2>

        {/* CSV File 1 - News Data Upload */}
        <div
          className={`w-full p-6 border-2 border-dashed rounded-lg ${
            isDragging ? "border-emerald-400 bg-gray-800" : "border-gray-700 bg-gray-950"
          } transition-all duration-300 mb-6`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop(setCsvFile1)}
        >
          <p className="text-center text-gray-400 mb-4">Drag & Drop News Data CSV file here</p>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange(setCsvFile1)}
            className="hidden"
            id="csvFile1"
          />
          <label
            htmlFor="csvFile1"
            className="block w-full py-2 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-center rounded-lg cursor-pointer transition-all duration-300"
          >
            Browse
          </label>
          {csvFile1 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-300">Selected File: {csvFile1.name}</p>
              <button
                onClick={handleRemoveFile(setCsvFile1)}
                className="mt-2 text-sm text-red-500 hover:text-red-400 transition-all duration-300"
              >
                Remove File
              </button>
            </div>
          )}
        </div>

        {/* CSV File 2 - Company Stock Data Upload */}
        <div
          className={`w-full p-6 border-2 border-dashed rounded-lg ${
            isDragging ? "border-emerald-400 bg-gray-800" : "border-gray-700 bg-gray-950"
          } transition-all duration-300 mb-6`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop(setCsvFile2)}
        >
          <p className="text-center text-gray-400 mb-4">Drag & Drop Company Stock Data CSV here</p>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange(setCsvFile2)}
            className="hidden"
            id="csvFile2"
          />
          <label
            htmlFor="csvFile2"
            className="block w-full py-2 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-center rounded-lg cursor-pointer transition-all duration-300"
          >
            Browse
          </label>
          {csvFile2 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-300">Selected File: {csvFile2.name}</p>
              <button
                onClick={handleRemoveFile(setCsvFile2)}
                className="mt-2 text-sm text-red-500 hover:text-red-400 transition-all duration-300"
              >
                Remove File
              </button>
            </div>
          )}
        </div>

        <div className="w-full mb-6 flex items-start gap-4">
          {/* Decimal Value Input */}
          <div className="flex-1">
            <label htmlFor="decimalValue" className="block text-sm font-medium text-gray-400 mb-2">
              Enter ASPI:
            </label>
            <input
              type="number"
              step="0.01"
              id="decimalValue"
              value={decimalValue}
              onChange={(event) => setDecimalValue(event.target.value)}
              className="w-full p-3 bg-gray-950 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-all duration-300"
              placeholder="10000.00"
            />
          </div>

          {/* ASPI Date Picker */}
          <div className="flex-1">
            <label htmlFor="aspiDate" className="block text-sm font-medium text-gray-400 mb-2">
              Select ASPI Date:
            </label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !aspiDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {aspiDate ? format(aspiDate, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
              <Calendar
  mode="single"
  selected={aspiDate}
  onSelect={setAspiDate}
  initialFocus
  className="w-full border border-gray-800 rounded-lg bg-gray-900 text-gray-400"
  classNames={{
    day: "h-10 w-10 p-0 font-normal text-center",
    day_selected: "bg-emerald-500 text-white hover:bg-emerald-600",
    day_today: "font-semibold text-emerald-500",
    head_cell: "text-gray-400 font-medium text-center",
    nav_button: "h-8 w-8 bg-transparent text-gray-400 hover:bg-gray-800 rounded-md",
  }}
/>
              </PopoverContent>
            </Popover>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          className="w-full py-3 bg-gradient-to-r from-emerald-600 to-purple-700 text-white font-semibold rounded-lg hover:from-emerald-700 hover:to-purple-800 transition-all duration-300"
        >
          Analyze Data
        </button>
      </div>
    </div>
  );
}
