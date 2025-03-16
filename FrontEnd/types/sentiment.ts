export interface SentimentItem {
    date: string;
    positive: number;
    neutral: number;
    negative: number;
    weighted_score: number;
  }

 export interface SentimentData {
    daily: { name: string; value: number }[];
    weekly: { name: string; value: number }[];
  }
  
 export interface LineChartDataItem {
    date: string;
    sentiment: number;
  }