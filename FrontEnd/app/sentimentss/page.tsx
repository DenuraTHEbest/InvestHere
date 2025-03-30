"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useEffect } from 'react';

// Define the type for the sentiment data
type SentimentData = {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  weighted_score: number;
};

const SENTIMENT_COLORS = ['#10B981', '#6B7280', '#EF4444'];

export default function SentimentAnalysis() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'daily' | 'weekly'>('daily');
  const [data, setData] = useState<SentimentData[]>([]);
  const [lineChartData, setLineChartData] = useState<{ date: string; sentiment: number }[]>([]);
  const [sentimentSummary, setSentimentSummary] = useState<{ name: string; value: number }[]>([]);

  // Fetch data from Flask API
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
  }, [selectedTimeframe]); // 👈 Trigger when `selectedTimeframe` changes

  return (
    <div className="min-h-screen bg-background font-sans">
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
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
                            label
                          >
                            {sentimentSummary.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index]} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend/>
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
                            name="Sentiment Score"
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
        </div>
      </main>
    </div>
  );
}
