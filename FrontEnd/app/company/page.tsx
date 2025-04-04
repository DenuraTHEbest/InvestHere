"use client";

import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { SearchIcon, ArrowUpIcon, ArrowDownIcon } from "lucide-react";

// Define the shape of each document from MongoDB.
interface CompanyDoc {
  _id: string;
  Company_Name: string;
  Date: string;
  Actual_Final: number;
  // Allow any additional fields (Predicted_Day_1, Predicted_Day_2, etc.)
  [key: string]: any;
}

// Define the shape for chart data.
interface ChartData {
  label: string;
  value: number | null;
}

// Build chart data for Recharts from a single document.
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

// Calculate a simple performance metric comparing Predicted Day 1 to Actual_Final.
function calculatePerformance(doc: CompanyDoc): number {
  const actual = doc.Actual_Final;
  const predicted = doc["Predicted_Day_1"];
  if (typeof actual !== "number" || typeof predicted !== "number") {
    return 0;
  }
  return ((predicted - actual) / actual) * 100;
}

export default function CompanyPredictions() {
  const [companyData, setCompanyData] = useState<CompanyDoc[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  // On component mount, fetch all documents from your Node/Express server.
  useEffect(() => {
    fetch("http://localhost:5002/api/predictions")
      .then((res) => res.json())
      .then((data: CompanyDoc[]) => {
        console.log("Fetched data from server:", data);
        setCompanyData(data);
      })
      .catch((err) => console.error("Error fetching data:", err));
  }, []);

  // Sort everything by performance (descending).
  const sortedByPerformance = [...companyData].sort(
    (a, b) => calculatePerformance(b) - calculatePerformance(a)
  );

  // 1) BEST PERFORMING STOCKS: Top four by performance
  const topFour = sortedByPerformance.slice(0, 4);

  // 2) STOCK PRICE PREDICTIONS: Use *your custom list* of companies for the tabs
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

  // Filter the full dataset to only those in the tabCompanies list.
  const allTabDocs = companyData.filter((doc) =>
    tabCompanies.includes(doc.Company_Name)
  );

  // Apply the searchTerm to the filtered list
  const filteredTabDocs = allTabDocs.filter((doc) =>
    doc.Company_Name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 p-4 md:p-8">
      {/* ================== BEST PERFORMING STOCKS ================== */}
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
                      {/* Display Predicted (Day 1) and Actual values */}
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

      {/* ================== STOCK PRICE PREDICTIONS (Tabs) ================== */}
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
                  <TabsContent
                    key={doc._id}
                    value={doc._id}
                    className="h-[300px]"
                  >
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
