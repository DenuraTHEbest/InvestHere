"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpIcon, ArrowDownIcon, LineChartIcon } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell } from 'recharts';
import { TrendingUpIcon, MessageCircleIcon, SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from 'next/link';
import { FormatString } from 'mongoose';

//import { ASPI } from './aspi'; // Import the ASPI component

//convert the date to a readable format
function formatDate(date: string) {
  return new Date(date).toLocaleDateString();
}

// Convert a date string (e.g., "2024-03-13") to "13/3/2024"
function formatDateToDDMMYYYY(dateString: string): string {
  const date = new Date(dateString); // Parse the date string
  const day = date.getDate(); // Get the day (1-31)
  const month = date.getMonth() + 1; // Get the month (0-11, so add 1)
  const year = date.getFullYear(); // Get the year (e.g., 2024)

  return `${day}/${month}/${year}`; // Format as DD/MM/YYYY
}

// Define the type for the ASPI data
type ASPIData = {
  date: string;
  actual: number | null; // Allow null for missing actual values
  predicted: number;
};

export function ASPI() {
  // State for ASPI data
  const [aspiData, setAspiData] = useState({
    daily: {
      current: 0,
      predicted: 0,
      change: 0,
      date: '',
    },
  });

  //State for storing historical and predicted ASPI data for the chart
  const [aspiprogressData, setAspiProgressData] = useState<ASPIData[]>([]);

  // Fetch ASPI data from the backend
  // Fetch ASPI data from the backend
useEffect(() => {
  const apiUrl = 'http://localhost:5000/';
  const today = new Date("2024-05-16"); // Hypothetical today

  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      console.log("Fetched data from backend:", data); // Debugging: Log fetched data

      // Transform the data into the format your frontend expects
      // const transformedData = data.map((item: any) => ({
      //   date: formatDateToDDMMYYYY(item.Date), // Format the date as DD/MM/YYYY
      //   actual: item.Actual_Day_1 || null, // Use null if Actual_Day_1 is missing
      //   predicted: item.Predicted_Day_1,
      // }));

      //transformeddate is equal to data
      const transformedData = data;

      // Find the last actual value
      const lastActualData = [...transformedData].reverse().find(item => item.actual !== null);
      const lastActualDate = lastActualData?.date || null;
      const lastActualValue = lastActualData?.actual || 0;

      // Find the next trading day (first day with a predicted value after the last actual value)
      const nextTradingDay = transformedData.find((item: ASPIData) => item.date > lastActualDate && item.predicted !== null);
      const nextTradingDayDate = nextTradingDay?.date || null;
      const nextTradingDayPredicted = nextTradingDay?.predicted || 0;

      // Calculate the increment percentage
      const increment = lastActualValue
        ? parseFloat(((nextTradingDayPredicted - lastActualValue) / lastActualValue * 100).toFixed(2))
        : 0;

      console.log("Last actual data:", lastActualData); // Debugging: Log last actual data
      console.log("Next trading day:", nextTradingDay); // Debugging: Log next trading day
      console.log("Increment percentage:", increment); // Debugging: Log increment percentage

      // Update the aspiData object
      setAspiData({
        daily: {
          current: lastActualValue, // Last actual value
          predicted: nextTradingDayPredicted, // Next trading day's predicted value
          change: increment, // Increment percentage
          date: nextTradingDayDate, // Next trading day's date
        },
      });

      // Prepare data for the graph
      const graphData = transformedData.map((item: ASPIData) => ({
        date: formatDateToDDMMYYYY(item.date), // Format the date as DD/MM/YYYY
        actual: item.date <= lastActualDate ? item.actual : null, // Show actual values until the last actual date
        predicted: parseFloat(item.predicted.toFixed(2)), // Format predicted to 2 decimal places
      }));

      console.log("Graph data:", graphData); // Debugging: Log graph data

      // Update the aspiprogressData array
      setAspiProgressData(graphData);
    })
    .catch(error => {
      console.error('Error fetching ASPI data:', error);
    });
}, []);

  console.log("ASPI Data:", aspiData);
  console.log("ASPI Progress Data:", aspiprogressData);
  return (
    <>
      {/* ASPI Prediction Card */}
      <Card className="col-span-full md:col-span-1">
        <CardHeader>
          <CardTitle>ASPI Prediction</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="daily">
            <TabsList className="mb-4">
              <TabsTrigger value="daily">Daily</TabsTrigger>
            </TabsList>
            <TabsContent value="daily">
            <div className="space-y-4">
  <div className="flex items-center justify-between">
    <div>
    <p className="text-2xl font-bold">
  {aspiData.daily.predicted !== undefined ? aspiData.daily.predicted.toFixed(2) : "--"}
</p>
<div className={`flex items-center gap-1 ${aspiData.daily.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
  {aspiData.daily.change >= 0 ? (
    <ArrowUpIcon className="h-4 w-4" />
  ) : (
    <ArrowDownIcon className="h-4 w-4" />
  )}
  <span>{Math.abs(aspiData.daily.change).toFixed(2)}%</span>
</div>
    </div>
    <LineChartIcon className="h-12 w-12 text-muted-foreground" />
  </div>
  <p className="text-sm text-muted-foreground">
    Prediction for: {aspiData.daily.date}
  </p>
</div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* ASPI Progress Chart */}
      <Card className="col-span-full md:col-span-2">
        <CardHeader>
          <CardTitle>ASPI Progress</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
  <LineChart data={aspiprogressData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis domain={['auto', 'auto']} />
    <Tooltip />
    <Line 
      type="monotone" 
      dataKey="actual" 
      stroke="hsl(var(--chart-2))" 
      strokeWidth={2}
      name="Actual"
    />
    <Line 
      type="monotone" 
      dataKey="predicted" 
      stroke="hsl(var(--chart-3))" 
      strokeWidth={2}
      name="Predicted"
      strokeDasharray="5 5"
    />
  </LineChart>
</ResponsiveContainer>
        </CardContent>
      </Card>
    </>
  );
}

// Define the type for the sentiment data
type SentimentData = {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  weighted_score: number;
};

const SENTIMENT_COLORS = ['#10B981', '#6B7280', '#EF4444'];

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState<'daily' | 'weekly'>('daily');
  const [data, setData] = useState<SentimentData[]>([]);
  const [lineChartData, setLineChartData] = useState<{ date: string; sentiment: number }[]>([]);
  const [sentimentSummary, setSentimentSummary] = useState<{ name: string; value: number }[]>([]);

  const stockPredictions = [
    { name: "SAMP.N", current: 245.50, predicted: 252.30, change: 2.77, performance: 95 },
    { name: "DIAL.N", current: 89.75, predicted: 85.20, change: -5.07, performance: 82 },
    { name: "COMB.N", current: 156.25, predicted: 162.80, change: 4.19, performance: 88 },
    { name: "VONE.N", current: 312.90, predicted: 318.45, change: 1.77, performance: 91 },
  ].sort((a, b) => b.performance - a.performance);

  const filteredStocks = stockPredictions.filter(stock => 
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Mock data for stock historical data
  const stockHistoricalData: Record<string, { date: string; actual: number; predicted: number }[]> = {
    "SAMP.N": [
      { date: "2023-10-01", actual: 240, predicted: 245 },
      { date: "2023-10-02", actual: 245, predicted: 250 },
    ],
    "DIAL.N": [
      { date: "2023-10-01", actual: 90, predicted: 88 },
      { date: "2023-10-02", actual: 89, predicted: 87 },
    ],
    "COMB.N": [
      { date: "2023-10-01", actual: 155, predicted: 160 },
      { date: "2023-10-02", actual: 156, predicted: 162 },
    ],
    "VONE.N": [
      { date: "2023-10-01", actual: 310, predicted: 315 },
      { date: "2023-10-02", actual: 312, predicted: 318 },
    ],
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const endpoint = selectedTimeframe === 'daily'
          ? 'http://127.0.0.1:5000/get-daily-sentiment'
          : 'http://127.0.0.1:5000/get-weekly-sentiment';

        const response = await fetch(endpoint);
        const result: SentimentData[] = await response.json();
        setData(result);

        // Aggregate sentiment data for pie chart
        const summary = [
          { name: "Positive", value: result.reduce((sum, d) => sum + d.positive, 0) },
          { name: "Neutral", value: result.reduce((sum, d) => sum + d.neutral, 0) },
          { name: "Negative", value: result.reduce((sum, d) => sum + d.negative, 0) },
        ];
        setSentimentSummary(summary);

        // Prepare data for line chart
        const lineData = result.map((d) => ({
          date: new Date(d.date).toLocaleDateString(),
          sentiment: d.weighted_score,
        }));
        setLineChartData(lineData);

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [selectedTimeframe]);

  return (
    <div className="min-h-screen bg-background font-sans">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <TrendingUpIcon className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold text-primary">InvestHere</h1>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Link 
              href="/chat" 
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <MessageCircleIcon className="h-4 w-4" />
              <span>Open Chatbot</span>
            </Link>
          </div>
        </div>
      </header>

      <section className="bg-gradient-to-b from-primary/5 to-background py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">Advanced Stock Market Predictions</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Make informed investment decisions with our AI-powered market analysis and real-time sentiment tracking.
          </p>
        </div>
      </section>

      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Sentiment Analysis Card */}
          <Card className="col-span-full">
            <CardHeader>
              <CardTitle>Market Sentiment Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="daily" className="w-full">
                <TabsList>
                  <TabsTrigger 
                    value="daily" 
                    onClick={() => setSelectedTimeframe('daily')}
                  >
                    Daily
                  </TabsTrigger>
                  <TabsTrigger 
                    value="weekly" 
                    onClick={() => setSelectedTimeframe('weekly')}
                  >
                    Weekly
                  </TabsTrigger>
                </TabsList>
                
                {/* Daily Sentiment */}
                <TabsContent value="daily" className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Pie Chart */}
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentSummary}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {sentimentSummary.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Line Chart */}
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={lineChartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[-1, 1]} />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="sentiment"
                            stroke="#3b82f6"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </TabsContent>

                {/* Weekly Sentiment */}
                <TabsContent value="weekly" className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Pie Chart */}
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentSummary}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {sentimentSummary.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Line Chart */}
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={lineChartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[-1, 1]} />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="sentiment"
                            stroke="#3b82f6"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* ASPI Component */}
          <ASPI />

          {/* Best Performing Stocks */}
          <Card className="col-span-full">
            <CardHeader>
              <CardTitle>Best Performing Stocks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                {stockPredictions.slice(0, 4).map((stock) => (
                  <div key={stock.name} className="p-4 rounded-lg bg-muted">
                    <h3 className="font-semibold">{stock.name}</h3>
                    <div className="mt-2 space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Performance</span>
                        <span className="font-medium">{stock.performance}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Predicted</span>
                        <span className="font-medium">Rs. {stock.predicted.toFixed(2)}</span>
                      </div>
                      <div className={`flex items-center gap-1 text-sm ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {stock.change >= 0 ? (
                          <ArrowUpIcon className="h-3 w-3" />
                        ) : (
                          <ArrowDownIcon className="h-3 w-3" />
                        )}
                        <span>{Math.abs(stock.change).toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Stock Price Predictions with Search */}
          <Card className="col-span-full">
            <CardHeader>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <CardTitle>Stock Price Predictions</CardTitle>
                <div className="relative w-full md:w-64">
                  <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search stocks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue={filteredStocks[0]?.name} className="w-full">
                <TabsList className="w-full justify-start overflow-x-auto">
                  {filteredStocks.map((stock) => (
                    <TabsTrigger key={stock.name} value={stock.name}>
                      {stock.name}
                    </TabsTrigger>
                  ))}
                </TabsList>
                {filteredStocks.map((stock) => (
                  <TabsContent key={stock.name} value={stock.name} className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={stockHistoricalData[stock.name] || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis domain={['auto', 'auto']} />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="actual" 
                          stroke="hsl(var(--chart-4))" 
                          strokeWidth={2}
                          name="Actual"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="predicted" 
                          stroke="hsl(var(--chart-5))" 
                          strokeWidth={2}
                          name="Predicted"
                          strokeDasharray="5 5"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}