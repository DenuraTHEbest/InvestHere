'use client'
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement } from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

const data = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
  datasets: [
    {
      label: "ASPI Index",
      data: [6500, 6700, 6600, 6800, 7000, 6900, 7100],
      borderColor: "#4CAF50",
      backgroundColor: "rgba(76, 175, 80, 0.2)",
      fill: true,
    },
  ],
};

export default function Home() {
  return (
    <div style={{ backgroundColor: '#121212', color: '#ffffff', minHeight: '100vh', padding: '20px' }}>
      <nav style={{ display: 'flex', alignItems: 'center', padding: '10px', background: '#1e1e1e', borderRadius: '10px' }}>
        <img src="/logo.png" alt="Logo" style={{ height: '40px', marginRight: '10px' }} />
        <h1>InvestHERE</h1>
      </nav>
      <section style={{ textAlign: 'center', padding: '50px 20px', background: '#1e1e1e', borderRadius: '10px', margin: '20px 0' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 'bold', marginBottom: '10px' }}>Track the Market Like a Pro</h1>
        <p style={{ fontSize: '1.2rem', color: '#bbb' }}>Stay updated with the best-performing stocks in real time.</p>
      </section>
      <main style={{ marginTop: '20px' }}>
        <h1>Top Performing Companies</h1>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', width: '300px', textAlign: 'center' }}>
            <h3>Company A</h3>
            <p>Stock Price: $250</p>
            <p>Change: +5.2%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', width: '300px', textAlign: 'center' }}>
            <h3>Company B</h3>
            <p>Stock Price: $180</p>
            <p>Change: +3.8%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', width: '300px', textAlign: 'center' }}>
            <h3>Company C</h3>
            <p>Stock Price: $320</p>
            <p>Change: +6.1%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', width: '300px', textAlign: 'center' }}>
            <h3>Company D</h3>
            <p>Stock Price: $380</p>
            <p>Change: +6.8%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', width: '300px', textAlign: 'center' }}>
            <h3>Company E</h3>
            <p>Stock Price: $170</p>
            <p>Change: +8.1%</p>
          </div>
        </div>
        <section style={{ marginTop: '40px', padding: '20px', background: '#1e1e1e', borderRadius: '10px', maxWidth: '500px',maxHeight: '500px', marginLeft: 'auto', marginRight: 'auto' }}>
          <h2 style={{ textAlign: 'center' }}>ASPI Index Performance</h2>
          <Line data={data} options={{ maintainAspectRatio: false }} width={400} height={300} />
        </section>
      </main>
      <footer style={{ textAlign: 'center', padding: '10px', background: '#1e1e1e', borderRadius: '10px', marginTop: '20px' }}>
        <p>&copy; 2025 Stock Market. All rights reserved.</p>
      </footer>
    </div>
  );
}
