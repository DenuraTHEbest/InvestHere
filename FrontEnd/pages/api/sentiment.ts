import type { NextApiRequest, NextApiResponse } from 'next';
import dbConnect from '../../lib/mongodb';
import Sentiment from '../../models/Sentiment';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  await dbConnect();

  try {
    const daily = await Sentiment.find()
      .sort({ date: -1 })
      .limit(30); // Last 30 days
    const weekly = await Sentiment.aggregate([
      {
        $group: {
          _id: { $week: "$date" },
          positive: { $sum: "$positive" },
          negative: { $sum: "$negative" },
          neutral: { $sum: "$neutral" },
          total: { $sum: "$total" },
          weighted_score: { $avg: "$weighted_score" },
        },
      },
      { $sort: { _id: -1 } },
      { $limit: 10 },
    ]);

    res.status(200).json({ daily, weekly });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch sentiment data' });
  }
}
