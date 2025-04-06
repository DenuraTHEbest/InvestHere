"use client";

import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import {
  ArrowUpIcon,
  ArrowDownIcon,
  LineChartIcon,
  TrendingUpIcon,
  MessageCircleIcon,
  SearchIcon,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

// ---------------------------
// Utility Functions
// ---------------------------

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

// ---------------------------
// Types for Original Data
// ---------------------------

type ASPIData = {
  date: string;
  actual: number | null;
  predicted: number;
};

type SentimentData = {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  weighted_score: number;
};

type TimeframeData = {
  rawData: SentimentData[];
  pieData: { name: string; value: number }[];
  lineData: { date: string; sentiment: number }[];
};

// ---------------------------
// Components
// ---------------------------

// ASPI Prediction Component
function ASPIPrediction() {
  const [aspiData, setAspiData] = useState({
    daily: {
      current: 0,
      predicted: 0,
      change: 0,
      date: "",
    },
  });

  useEffect(() => {
    const apiUrl = "http://localhost:5050";
    const today = new Date("2024-05-16");

    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched data from backend:", data);

        const transformedData = data;
        const lastActualData = [...transformedData]
          .reverse()
          .find((item: ASPIData) => item.actual !== null);
        const lastActualDate = lastActualData?.date || null;
        const lastActualValue = lastActualData?.actual || 0;

        const nextTradingDay = transformedData.find(
          (item: ASPIData) => item.date > lastActualDate && item.predicted !== null
        );
        const nextTradingDayDate = nextTradingDay?.date || null;
        const nextTradingDayPredicted = nextTradingDay?.predicted || 0;

        const increment = lastActualValue
          ? parseFloat(
              (
                ((nextTradingDayPredicted - lastActualValue) / lastActualValue) *
                100
              ).toFixed(2)
            )
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
      .catch((error) => {
        console.error("Error fetching ASPI data:", error);
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
                    {aspiData.daily.predicted !== undefined
                      ? aspiData.daily.predicted.toFixed(2)
                      : "--"}
                  </p>
                  <div
                    className={`flex items-center gap-1 ${
                      aspiData.daily.change >= 0
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
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
    const apiUrl = "http://localhost:5050";
    const today = new Date("2024-05-16");

    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched data from backend:", data);

        const transformedData = data;
        const lastActualData = [...transformedData]
          .reverse()
          .find((item: ASPIData) => item.actual !== null);
        const lastActualDate = lastActualData?.date || null;

        const graphData = transformedData.map((item: ASPIData) => ({
          date: formatDateToDDMMYYYY(item.date),
          actual: item.date <= lastActualDate ? item.actual : null,
          predicted: parseFloat(item.predicted.toFixed(2)),
        }));

        setAspiProgressData(graphData);
      })
      .catch((error) => {
        console.error("Error fetching ASPI data:", error);
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
            <YAxis domain={["auto", "auto"]} />
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

// PieChart and LineChart Containers for Market Sentiment Analysis
const SENTIMENT_COLORS = ["#10B981", "#6B7280", "#EF4444"];

const PieChartContainer = ({
  data,
}: {
  data: { name: string; value: number }[];
}) => (
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

const LineChartContainer = ({
  data,
}: {
  data: { date: string; sentiment: number }[];
}) => (
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

// Dashboard Component
function Dashboard() {
  const [activeTab, setActiveTab] = useState<"daily" | "weekly">("daily");
  const [dailyData, setDailyData] = useState<TimeframeData>({
    rawData: [],
    pieData: [],
    lineData: [],
  });
  const [weeklyData, setWeeklyData] = useState<TimeframeData>({
    rawData: [],
    pieData: [],
    lineData: [],
  });
  const [isLoading, setIsLoading] = useState({
    daily: true,
    weekly: true,
  });

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        // Fetch daily sentiment data
        const dailyResponse = await fetch("http://127.0.0.1:5000/get-daily-sentiment");
        const dailyResult: SentimentData[] = await dailyResponse.json();
        processData(dailyResult, "daily");

        // Fetch weekly sentiment data
        const weeklyResponse = await fetch("http://127.0.0.1:5000/get-weekly-sentiment");
        const weeklyResult: SentimentData[] = await weeklyResponse.json();
        processData(weeklyResult, "weekly");
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchAllData();
  }, []);

  const processData = (rawData: SentimentData[], timeframe: "daily" | "weekly") => {
    const sortedData = [...rawData].sort((a, b) =>
      a.date.localeCompare(b.date)
    );

    const pieData = [
      { name: "Positive", value: sortedData.reduce((sum, d) => sum + d.positive, 0) },
      { name: "Neutral", value: sortedData.reduce((sum, d) => sum + d.neutral, 0) },
      { name: "Negative", value: sortedData.reduce((sum, d) => sum + d.negative, 0) },
    ];

    const lineData = sortedData.map((d) => ({
      date:
        timeframe === "daily"
          ? new Date(d.date).toLocaleDateString()
          : d.date,
      sentiment: d.weighted_score,
    }));

    if (timeframe === "daily") {
      setDailyData({ rawData: sortedData, pieData, lineData });
      setIsLoading((prev) => ({ ...prev, daily: false }));
    } else {
      setWeeklyData({ rawData: sortedData, pieData, lineData });
      setIsLoading((prev) => ({ ...prev, weekly: false }));
    }
  };

  const currentData = activeTab === "daily" ? dailyData : weeklyData;
  const currentLoading = activeTab === "daily" ? isLoading.daily : isLoading.weekly;

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
                onValueChange={(value) => setActiveTab(value as "daily" | "weekly")}
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

          {/* ASPI Prediction and Progress */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ASPIPrediction />
            <ASPIProgress />
            <div className="hidden md:block"></div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Types and utility functions for company predictions from MongoDB.
interface CompanyDoc {
  _id: string;
  Company_Name: string;
  Date: string;
  Actual_Final: number;
  [key: string]: any;
}

interface ChartData {
  label: string;
  value: number | null;
}

function buildChartData(doc: CompanyDoc): ChartData[] {
  // Start with the Actual value as "Day 0".
  const chartData: ChartData[] = [
    { label: "Day 0 (Actual)", value: doc.Actual_Final ?? null },
  ];

  // Loop through days 1 to 20 and add predicted values if they exist.
  for (let i = 1; i <= 20; i++) {
    const key = `Predicted_Day_${i}`;
    if (doc[key] !== undefined) {
      chartData.push({ label: `Day ${i}`, value: doc[key] });
    }
  }
  return chartData;
}

function calculatePerformance(doc: CompanyDoc): number {
  const actual = doc.Actual_Final;
  const predicted = doc["Predicted_Day_1"];
  if (typeof actual !== "number" || typeof predicted !== "number") {
    return 0;
  }
  return ((predicted - actual) / actual) * 100;
}

function CompanyPredictions() {
  const [companyData, setCompanyData] = useState<CompanyDoc[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch("http://localhost:5002/api/predictions")
      .then((res) => res.json())
      .then((data: CompanyDoc[]) => {
        console.log("Fetched data from server:", data);
        setCompanyData(data);
      })
      .catch((err) => console.error("Error fetching data:", err));
  }, []);

  // Sort documents by performance (descending).
  const sortedByPerformance = [...companyData].sort(
    (a, b) => calculatePerformance(b) - calculatePerformance(a)
  );
  const topFour = sortedByPerformance.slice(0, 4);

  // List of companies to be shown as tabs.
  const tabCompanies = [
    "ACCESS ENG SL_data",
    "AITKEN SPENCE_data",
    "ALUMEX PLC_dat",
    "CALT_data",
    "CANDOR OPP FUND_data",
    "CENTRAL FINANCE_data",
    "CEYLINCO INS._data",
    "CIC_data",
    "DFCC BANK PLC_data",
    "HNB_data",
    "HORANA_data",
    "JAT HOLDINGS_data",
    "JETWING SYMPHONY_data",
    "KANDY HOTELS_data",
    "ON'ALLY_data",
    "R I L PROPERTY _data",
    "RENUKA CITY HOT._data",
    "SARVODAYA DEVFIN_data",
    "SERENDIB LAND_data",
    "SEYLAN BANK_data",
    "TEA SMALLHOLDER_data",
    "TOKYO CEMENT_data",
    "TRADE FINANCE_data",
    "UNION ASSURANCE_data",
    "VALLIBEL_data",
  ];

  // Filter the dataset for the companies that match the list.
  const allTabDocs = companyData.filter((doc) =>
    tabCompanies.includes(doc.Company_Name)
  );

  // Apply search filter.
  const filteredTabDocs = allTabDocs.filter((doc) =>
    doc.Company_Name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 p-4 md:p-8">
      {/* ----------------- BEST PERFORMING STOCKS ----------------- */}
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Best Performing Stocks</CardTitle>
        </CardHeader>
        <CardContent>
          {topFour.length > 0 ? (
            <div className="grid md:grid-cols-4 gap-4">
              {topFour.map((doc) => {
                const perf = calculatePerformance(doc);
                return (
                  <div key={doc._id} className="p-4 rounded-lg bg-muted">
                    <h3 className="font-semibold">{doc.Company_Name}</h3>
                    <div className="mt-2 space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Performance</span>
                        <span className="font-medium">{perf.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Predicted (Day 1)</span>
                        <span className="font-medium">
                          Rs. {doc["Predicted_Day_1"]?.toFixed(2) ?? "--"}
                        </span>
                      </div>
                      <div
                        className={`flex items-center gap-1 ${
                          perf >= 0 ? "text-green-500" : "text-red-500"
                        }`}
                      >
                        {perf >= 0 ? (
                          <ArrowUpIcon className="h-3 w-3" />
                        ) : (
                          <ArrowDownIcon className="h-3 w-3" />
                        )}
                        <span>{Math.abs(perf).toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p>No data yet...</p>
          )}
        </CardContent>
      </Card>

      {/* ----------------- STOCK PRICE PREDICTIONS (Tabs) ----------------- */}
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
          {filteredTabDocs.length > 0 ? (
            <Tabs defaultValue={filteredTabDocs[0]?._id} className="w-full">
              <TabsList className="w-full justify-start overflow-x-auto">
                {filteredTabDocs.map((doc) => (
                  <TabsTrigger key={doc._id} value={doc._id}>
                    {doc.Company_Name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {filteredTabDocs.map((doc) => {
                const dataForChart = buildChartData(doc);
                return (
                  <TabsContent key={doc._id} value={doc._id} className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={dataForChart}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="label" />
                        <YAxis domain={["auto", "auto"]} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke="#82ca9d"
                          strokeWidth={2}
                          name="Price"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </TabsContent>
                );
              })}
            </Tabs>
          ) : (
            <p>No stocks match your search.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Final Combined Dashboard Page
export default function DashboardPage() {
  return (
    <div>
      <Dashboard />
      <hr className="my-8" />
      <CompanyPredictions />
    </div>
  );
}