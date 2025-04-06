/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: '/api/rasa/:path*',
        destination: 'http://localhost:5005/:path*',
      },
    ];
  },
};

module.exports = nextConfig;