"use client";

import { useState } from 'react';

export default function CSVUploadPage() {
  // News sentiment data state
  const [newsFile, setNewsFile] = useState<File | null>(null);
  const [decimalValue, setDecimalValue] = useState<string>('');
  const [isDraggingNews, setIsDraggingNews] = useState<boolean>(false);

  // Company stock data state
  const [companyFile, setCompanyFile] = useState<File | null>(null);
  const [isDraggingCompany, setIsDraggingCompany] = useState<boolean>(false);

  // Generic file change handler
  const handleFileChange = (setter: (file: File | null) => void) => (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setter(event.target.files[0]);
    }
  };

  // Generic drag handlers accepting custom state setters
  const handleDragOver = (setter: (drag: boolean) => void) => (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setter(true);
  };

  const handleDragLeave = (setter: (drag: boolean) => void) => () => {
    setter(false);
  };

  const handleDrop = (
    fileSetter: (file: File | null) => void,
    dragSetter: (drag: boolean) => void
  ) => (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragSetter(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      fileSetter(event.dataTransfer.files[0]);
    }
  };

  const handleRemoveFile = (setter: (file: File | null) => void) => () => {
    setter(null);
  };

  const handleDecimalChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDecimalValue(event.target.value);
  };

  const handleSubmit = async () => {
    // Process news sentiment file if provided
    if (newsFile) {
      const formDataNews = new FormData();
      // The Flask endpoint expects the file under 'file1'
      formDataNews.append('file1', newsFile);
      // Optionally, add the decimal value if your backend needs it
      formDataNews.append('decimal', decimalValue);

      try {
        const responseNews = await fetch('http://127.0.0.1:5000/process_news', {
          method: 'POST',
          body: formDataNews,
        });
        const dataNews = await responseNews.json();
        console.log('News Data Response:', dataNews);
        if (responseNews.status === 200 && dataNews.status === 'success') {
          alert(dataNews.message || 'News file uploaded and processed successfully!');
        } else {
          alert(dataNews.message || 'Failed to process news file');
        }
      } catch (error) {
        console.error('Error uploading news file:', error);
        alert(`Failed to upload news file: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    // Process company stock data file if provided
    if (companyFile) {
      const formDataCompany = new FormData();
      // The Flask endpoint expects the file under 'file'
      formDataCompany.append('file', companyFile);

      try {
        const responseCompany = await fetch('http://127.0.0.1:5002/analyze_data', {
          method: 'POST',
          body: formDataCompany,
        });
        const dataCompany = await responseCompany.json();
        console.log('Company Data Response:', dataCompany);
        if (responseCompany.status === 200 && dataCompany.status === 'success') {
          alert(dataCompany.message || 'Company data file uploaded and processed successfully!');
        } else {
          alert(dataCompany.message || 'Failed to process company data file');
        }
      } catch (error) {
        console.error('Error uploading company data file:', error);
        alert(`Failed to upload company data file: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    // Inform the user if no files were provided
    if (!newsFile && !companyFile) {
      alert("Please select at least one file to upload.");
    }

    // Optionally, refresh the page or reset state here
    // window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex flex-col items-center justify-center p-6 text-white">
      <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-purple-500">
        Advanced Stock Market Predictions Admin Page
      </h1>

      <div className="w-full max-w-2xl bg-gray-900 rounded-lg p-8 shadow-lg border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6 text-gray-200">Upload Market Data</h2>

        {/* News Data Upload Section */}
        <div className="mb-8">
          <h3 className="text-xl font-medium text-gray-200 mb-4">News Data Upload</h3>
          <div
            className={`w-full p-6 border-2 border-dashed rounded-lg ${isDraggingNews ? 'border-emerald-400 bg-gray-800' : 'border-gray-700 bg-gray-950'} transition-all duration-300 mb-6`}
            onDragOver={handleDragOver(setIsDraggingNews)}
            onDragLeave={handleDragLeave(setIsDraggingNews)}
            onDrop={handleDrop(setNewsFile, setIsDraggingNews)}
          >
            <p className="text-center text-gray-400 mb-4">Drag &amp; Drop News Data CSV file here</p>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange(setNewsFile)}
              className="hidden"
              id="newsFile"
            />
            <label
              htmlFor="newsFile"
              className="block w-full py-2 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-center rounded-lg cursor-pointer transition-all duration-300"
            >
              Browse
            </label>
            {newsFile && (
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-300">Selected File: {newsFile.name}</p>
                <button
                  onClick={handleRemoveFile(setNewsFile)}
                  className="mt-2 text-sm text-red-500 hover:text-red-400 transition-all duration-300"
                >
                  Remove File
                </button>
              </div>
            )}
          </div>
          {/* Decimal value input for news data */}
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
        </div>

        {/* Company Stock Data Upload Section */}
        <div className="mb-8">
          <h3 className="text-xl font-medium text-gray-200 mb-4">Company Stock Data Upload</h3>
          <div
            className={`w-full p-6 border-2 border-dashed rounded-lg ${isDraggingCompany ? 'border-emerald-400 bg-gray-800' : 'border-gray-700 bg-gray-950'} transition-all duration-300 mb-6`}
            onDragOver={handleDragOver(setIsDraggingCompany)}
            onDragLeave={handleDragLeave(setIsDraggingCompany)}
            onDrop={handleDrop(setCompanyFile, setIsDraggingCompany)}
          >
            <p className="text-center text-gray-400 mb-4">Drag &amp; Drop Company Stock Data CSV here</p>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange(setCompanyFile)}
              className="hidden"
              id="companyFile"
            />
            <label
              htmlFor="companyFile"
              className="block w-full py-2 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-center rounded-lg cursor-pointer transition-all duration-300"
            >
              Browse
            </label>
            {companyFile && (
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-300">Selected File: {companyFile.name}</p>
                <button
                  onClick={handleRemoveFile(setCompanyFile)}
                  className="mt-2 text-sm text-red-500 hover:text-red-400 transition-all duration-300"
                >
                  Remove File
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button for Both */}
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