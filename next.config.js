/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    USE_LOCAL_MOCK: process.env.USE_LOCAL_MOCK || 'true',
  },
}

module.exports = nextConfig