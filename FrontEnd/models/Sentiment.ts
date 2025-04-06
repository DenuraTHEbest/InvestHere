import mongoose from 'mongoose';

const SentimentSchema = new mongoose.Schema({
  date: { type: Date, required: true },
  negative: { type: Number, required: true },
  neutral: { type: Number, required: true },
  positive: { type: Number, required: true },
  total: { type: Number, required: true },
  weighted_score: { type: Number, required: true },
});

const Sentiment = mongoose.models.Sentiment || mongoose.model('Sentiment', SentimentSchema);

export default Sentiment;
