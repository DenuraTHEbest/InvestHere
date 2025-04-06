"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useEffect } from 'react';

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

export default function SentimentAnalysis() {
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
        : d.date, // Use the week string directly for weekly data
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
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
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
        </div>
      </main>
    </div>
  );
}

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
          name="Sentiment Score"
          stroke="#3b82f6"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);