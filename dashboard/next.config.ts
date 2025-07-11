/** @type {import('next').NextConfig} */
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/praetor/:path*',
        destination: `http://localhost:5000/api/praetor/:path*`,
      },
    ]
  },
}
