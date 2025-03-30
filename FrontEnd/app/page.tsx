"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useEffect } from 'react';
import { ArrowUpIcon, ArrowDownIcon, LineChartIcon, TrendingUpIcon, MessageCircleIcon, SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from 'next/link';

// Convert the date to a readable format
function formatDate(date: string) {
  return new Date(date).toLocaleDateString();
}

// Convert a date string (e.g., "2024-03-13") to "13/3/2024"
function formatDateToDDMMYYYY(dateString: string): string {
  const date = new Date(dateString);
  const day = date.getDate();
  const month = date.getMonth() + 1;
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

// Define the type for the ASPI data
type ASPIData = {
  date: string;
  actual: number | null;
  predicted: number;
};

// ASPI Prediction Component
function ASPIPrediction() {
  const [aspiData, setAspiData] = useState({
    daily: {
      current: 0,
      predicted: 0,
      change: 0,
      date: '',
    },
  });

  useEffect(() => {
    const apiUrl = 'http://localhost:5050';
    const today = new Date("2024-05-16");

    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        console.log("Fetched data from backend:", data);

        const transformedData = data;

        const lastActualData = [...transformedData].reverse().find(item => item.actual !== null);
        const lastActualDate = lastActualData?.date || null;
        const lastActualValue = lastActualData?.actual || 0;

        const nextTradingDay = transformedData.find((item: ASPIData) => item.date > lastActualDate && item.predicted !== null);
        const nextTradingDayDate = nextTradingDay?.date || null;
        const nextTradingDayPredicted = nextTradingDay?.predicted || 0;

        const increment = lastActualValue
          ? parseFloat(((nextTradingDayPredicted - lastActualValue) / lastActualValue * 100).toFixed(2))
          : 0;

        setAspiData({
          daily: {
            current: lastActualValue,
            predicted: nextTradingDayPredicted,
            change: increment,
            date: nextTradingDayDate,
          },
        });
      })
      .catch(error => {
        console.error('Error fetching ASPI data:', error);
      });
  }, []);

  return (
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
  );
}

// ASPI Progress Component
function ASPIProgress() {
  const [aspiprogressData, setAspiProgressData] = useState<ASPIData[]>([]);

  useEffect(() => {
    const apiUrl = 'http://localhost:5050';
    const today = new Date("2024-05-16");

    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        console.log("Fetched data from backend:", data);

        const transformedData = data;

        const lastActualData = [...transformedData].reverse().find(item => item.actual !== null);
        const lastActualDate = lastActualData?.date || null;

        const graphData = transformedData.map((item: ASPIData) => ({
          date: formatDateToDDMMYYYY(item.date),
          actual: item.date <= lastActualDate ? item.actual : null,
          predicted: parseFloat(item.predicted.toFixed(2)),
        }));

        setAspiProgressData(graphData);
      })
      .catch(error => {
        console.error('Error fetching ASPI data:', error);
      });
  }, []);

  return (
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

type TimeframeData = {
  rawData: SentimentData[];
  pieData: { name: string; value: number }[];
  lineData: { date: string; sentiment: number }[];
};

// PieChart and LineChart Components
const PieChartContainer = ({ data }: { data: { name: string; value: number }[] }) => (
  <div className="h-[300px]">
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={5}
          dataKey="value"
          label
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

const LineChartContainer = ({ data }: { data: { date: string; sentiment: number }[] }) => (
  <div className="h-[300px]">
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={[-1, 1]} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="sentiment"
          name="Average Score"
          stroke="#3b82f6"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

// Main Component
export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'daily' | 'weekly'>('daily');
  const [dailyData, setDailyData] = useState<TimeframeData>({ 
    rawData: [], 
    pieData: [], 
    lineData: [] 
  });
  const [weeklyData, setWeeklyData] = useState<TimeframeData>({ 
    rawData: [], 
    pieData: [], 
    lineData: [] 
  });
  const [isLoading, setIsLoading] = useState({
    daily: true,
    weekly: true
  });

  const stockPredictions = [
    { name: "SAMP.N", current: 245.50, predicted: 252.30, change: 2.77, performance: 95 },
    { name: "DIAL.N", current: 89.75, predicted: 85.20, change: -5.07, performance: 82 },
    { name: "COMB.N", current: 156.25, predicted: 162.80, change: 4.19, performance: 88 },
    { name: "VONE.N", current: 312.90, predicted: 318.45, change: 1.77, performance: 91 },
  ].sort((a, b) => b.performance - a.performance);

  const filteredStocks = stockPredictions.filter(stock => 
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

  // Fetch both datasets on initial load
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        // Fetch daily data
        const dailyResponse = await fetch('http://127.0.0.1:5000/get-daily-sentiment');
        const dailyResult: SentimentData[] = await dailyResponse.json();
        processData(dailyResult, 'daily');

        // Fetch weekly data
        const weeklyResponse = await fetch('http://127.0.0.1:5000/get-weekly-sentiment');
        const weeklyResult: SentimentData[] = await weeklyResponse.json();
        processData(weeklyResult, 'weekly');
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchAllData();
  }, []);

  const processData = (rawData: SentimentData[], timeframe: 'daily' | 'weekly') => {
    const sortedData = [...rawData].sort((a, b) => 
      a.date.localeCompare(b.date)
    );

    const pieData = [
      { name: "Positive", value: sortedData.reduce((sum, d) => sum + d.positive, 0) },
      { name: "Neutral", value: sortedData.reduce((sum, d) => sum + d.neutral, 0) },
      { name: "Negative", value: sortedData.reduce((sum, d) => sum + d.negative, 0) },
    ];

    const lineData = sortedData.map((d) => ({
      date: timeframe === 'daily' 
        ? new Date(d.date).toLocaleDateString() 
        : d.date,
      sentiment: d.weighted_score,
    }));

    if (timeframe === 'daily') {
      setDailyData({ rawData: sortedData, pieData, lineData });
      setIsLoading(prev => ({ ...prev, daily: false }));
    } else {
      setWeeklyData({ rawData: sortedData, pieData, lineData });
      setIsLoading(prev => ({ ...prev, weekly: false }));
    }
  };

  const currentData = activeTab === 'daily' ? dailyData : weeklyData;
  const currentLoading = activeTab === 'daily' ? isLoading.daily : isLoading.weekly;

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
        <div className="grid gap-6">
          {/* Market Sentiment Analysis */}
          <Card className="col-span-full">
            <CardHeader>
              <CardTitle>Market Sentiment Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs 
                defaultValue="daily" 
                className="w-full"
                onValueChange={(value) => setActiveTab(value as 'daily' | 'weekly')}
              >
                <TabsList>
                  <TabsTrigger value="daily">Daily</TabsTrigger>
                  <TabsTrigger value="weekly">Weekly</TabsTrigger>
                </TabsList>
                
                <TabsContent value="daily" className="space-y-4">
                  {currentLoading ? (
                    <div className="flex justify-center items-center h-64">
                      <p>Loading daily data...</p>
                    </div>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-4">
                      <PieChartContainer data={dailyData.pieData} />
                      <LineChartContainer data={dailyData.lineData} />
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="weekly" className="space-y-4">
                  {currentLoading ? (
                    <div className="flex justify-center items-center h-64">
                      <p>Loading weekly data...</p>
                    </div>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-4">
                      <PieChartContainer data={weeklyData.pieData} />
                      <LineChartContainer data={weeklyData.lineData} />
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* ASPI Prediction and Progress as separate cards side by side */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ASPIPrediction />
            <ASPIProgress />
            {/* Placeholder for alignment - this will be empty but ensures the grid layout works */}
            <div className="hidden md:block"></div>
          </div>

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