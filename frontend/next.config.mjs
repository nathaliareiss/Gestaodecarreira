/** @type {import('next').NextConfig} */
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").trim().replace(/\/$/, "")

const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_BASE_URL}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
