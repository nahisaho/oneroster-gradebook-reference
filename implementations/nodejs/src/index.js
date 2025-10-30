const app = require('./app');
const logger = require('./utils/logger');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
  logger.info(`🚀 OneRoster Gradebook Service started`);
  logger.info(`📍 Server: http://${HOST}:${PORT}`);
  logger.info(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`📚 API Base: /ims/oneroster/v1p2`);
  logger.info(`🔐 OAuth Token: POST /oauth/token`);
});
