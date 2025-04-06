"use client";

import { useState } from 'react';

export default function DecimalInputPage() {
  const [decimalValue, setDecimalValue] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleDecimalChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDecimalValue(event.target.value);
  };

  const handleSubmit = async () => {
    if (!decimalValue) {
      alert("Please enter a decimal value");
      return;
    }

    setIsProcessing(true);
    
    try {
      const response = await fetch('http://127.0.0.1:5050/api/process_aspi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ decimalValue }),
      });

      const data = await response.json();
      
      if (response.status === 200 && data.status === 'success') {
        alert(`Success! Weighted score: ${data.weighted_score}`);
        console.log('Pipeline outputs:', {
          feature: data.feature_pipeline_output,
          admin: data.admin_pipeline_output
        });
      } else {
        alert(data.message || 'Failed to process decimal value');
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`An error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex flex-col items-center justify-center p-6 text-white">
      <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-purple-500">
        Decimal Value Processor
      </h1>

      <div className="w-full max-w-md bg-gray-900 rounded-lg p-8 shadow-lg border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6 text-gray-200">Enter Decimal Value</h2>

        <div className="w-full mb-6">
          <label htmlFor="decimalValue" className="block text-sm font-medium text-gray-400 mb-2">
            Decimal Value:
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

        <button
          onClick={handleSubmit}
          disabled={isProcessing}
          className={`w-full py-3 bg-gradient-to-r from-emerald-600 to-purple-700 text-white font-semibold rounded-lg hover:from-emerald-700 hover:to-purple-800 transition-all duration-300 ${
            isProcessing ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isProcessing ? 'Processing...' : 'Submit Decimal Value'}
        </button>
      </div>
    </div>
  );
}