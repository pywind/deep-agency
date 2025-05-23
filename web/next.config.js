/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */


import "./src/env.js";

// Using webpack for both development and production for better stability
// Turbopack has been disabled due to performance issues

// Determine if we're in production mode
const isProd = process.env.NODE_ENV === 'production';

/** @type {import("next").NextConfig} */
const config = {
  // Enable dev indicators in development, disable in production
  devIndicators: isProd ? false : {
    position: 'bottom-left',
  },

  // Security headers configuration
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Cross-Origin-Resource-Policy',
            value: 'same-site',
          },
        ],
      },
      {
        // Specific configuration for favicon
        source: '/favicon.ico',
        headers: [
          {
            key: 'Cross-Origin-Resource-Policy',
            value: 'same-site',
          },
        ],
      },
    ];
  },

  // For production mode
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /\.md$/,
      use: "raw-loader",
    });
    return config;
  },

  // ... rest of the configuration.
  output: "standalone",
};

export default config;
