/** @type {import('next').NextConfig} */
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL?.trim()

if (!apiBaseUrl) {
  throw new Error("NEXT_PUBLIC_API_URL nao foi definido.")
}

const apiDestino = apiBaseUrl.replace(/\/$/, "")

const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiDestino}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
