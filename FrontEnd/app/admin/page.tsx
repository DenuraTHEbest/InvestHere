"use client"

import { useState } from 'react';

export default function CSVUploadPage() {
  const [csvFile1, setCsvFile1] = useState<File | null>(null);
  const [csvFile2, setCsvFile2] = useState<File | null>(null);
  const [decimalValue, setDecimalValue] = useState<string>('');
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleFileChange = (setter: (file: File | null) => void) => (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setter(event.target.files[0]);
    }
  };

  const handleDecimalChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDecimalValue(event.target.value);
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

  const handleSubmit = () => {
    // Handle form submission here
    console.log('CSV File 1:', csvFile1);
    console.log('CSV File 2:', csvFile2);
    console.log('Decimal Value:', decimalValue);
    // Add your logic to process the files and decimal value
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex flex-col items-center justify-center p-6 text-white">
      <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-purple-500">
        Advanced Stock Market Predictions Admin Page
      </h1>

      <div className="w-full max-w-2xl bg-gray-900 rounded-lg p-8 shadow-lg border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6 text-gray-200">Upload Market Data</h2>

        {/* CSV File 1 - News data Upload */}
        <div
          className={`w-full p-6 border-2 border-dashed rounded-lg ${
            isDragging ? 'border-emerald-400 bg-gray-800' : 'border-gray-700 bg-gray-950'
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
            <p className="mt-4 text-center text-sm text-gray-300">Selected File: {csvFile1.name}</p>
          )}
        </div>

        {/* CSV File 2 - company stock data Upload */}
        <div
          className={`w-full p-6 border-2 border-dashed rounded-lg ${
            isDragging ? 'border-emerald-400 bg-gray-800' : 'border-gray-700 bg-gray-950'
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
            <p className="mt-4 text-center text-sm text-gray-300">Selected File: {csvFile2.name}</p>
          )}
        </div>

        {/* Decimal Value Input */}
        <div className="w-full mb-6">
          <label htmlFor="decimalValue" className="block text-sm font-medium text-gray-400 mb-2">
            Enter Decimal Value:
          </label>
          <input
            type="number"
            step="0.01"
            id="decimalValue"
            value={decimalValue}
            onChange={handleDecimalChange}
            className="w-full p-3 bg-gray-950 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-all duration-300"
            placeholder="0.00"
          />
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