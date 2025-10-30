require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const { token } = require('./middleware/auth');
const { notFound, errorHandler } = require('./middleware/errorHandler');
const logger = require('./utils/logger');
const db = require('./models');

// Import routes
const categoriesRoutes = require('./routes/categories');
const lineItemsRoutes = require('./routes/lineItems');
const resultsRoutes = require('./routes/results');
const studentsRoutes = require('./routes/students');

// Create Express app
const app = express();

/**
 * Security middleware
 */
app.use(helmet());

/**
 * CORS configuration
 */
const corsOptions = {
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400, // 24 hours
};
app.use(cors(corsOptions));

/**
 * Rate limiting
 */
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10), // 1 minute
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10), // 100 requests per minute
  message: {
    imsx_codeMajor: 'failure',
    imsx_severity: 'error',
    imsx_description: 'Too many requests, please try again later',
    imsx_codeMinor: 'rate_limit_exceeded',
  },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

/**
 * Body parsing middleware
 */
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

/**
 * Logging middleware
 */
app.use(morgan('combined', { stream: logger.stream }));

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
  });
});

/**
 * Root endpoint - API information
 */
app.get('/', (req, res) => {
  res.json({
    name: 'OneRoster Gradebook Service',
    version: '1.2.0',
    specification: 'IMS Global OneRoster v1.2',
    description: 'Reference implementation of OneRoster Gradebook Service',
    endpoints: {
      token: '/oauth/token',
      categories: '/ims/oneroster/v1p2/categories',
      lineItems: '/ims/oneroster/v1p2/lineItems',
      results: '/ims/oneroster/v1p2/results',
      students: '/ims/oneroster/v1p2/students',
    },
    documentation: 'https://www.imsglobal.org/spec/oneroster/v1p2',
  });
});

/**
 * OAuth 2.0 token endpoint
 */
app.post('/oauth/token', token);

/**
 * OneRoster API routes
 * Base path: /ims/oneroster/v1p2
 */
const API_BASE = '/ims/oneroster/v1p2';

app.use(`${API_BASE}/categories`, categoriesRoutes);
app.use(`${API_BASE}/lineItems`, lineItemsRoutes);
app.use(`${API_BASE}/results`, resultsRoutes);
app.use(`${API_BASE}/students`, studentsRoutes);

/**
 * 404 handler
 */
app.use(notFound);

/**
 * Global error handler
 */
app.use(errorHandler);

/**
 * Database connection and server startup
 */
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

async function startServer() {
  try {
    // Test database connection
    await db.sequelize.authenticate();
    logger.info('Database connection established successfully');

    // Start server
    const server = app.listen(PORT, HOST, () => {
      logger.info(`Server running on http://${HOST}:${PORT}`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
      logger.info(`API Base: ${API_BASE}`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
      logger.info('SIGTERM signal received: closing HTTP server');
      server.close(() => {
        logger.info('HTTP server closed');
        db.sequelize.close().then(() => {
          logger.info('Database connection closed');
          process.exit(0);
        });
      });
    });

    process.on('SIGINT', () => {
      logger.info('SIGINT signal received: closing HTTP server');
      server.close(() => {
        logger.info('HTTP server closed');
        db.sequelize.close().then(() => {
          logger.info('Database connection closed');
          process.exit(0);
        });
      });
    });

    return server;
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Start server if this file is run directly
if (require.main === module) {
  startServer();
}

module.exports = app;
