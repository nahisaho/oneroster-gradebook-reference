const fs = require('fs');
const path = require('path');
const { Sequelize } = require('sequelize');
const logger = require('../utils/logger');

// Import database config
const { sequelize } = require('../config/database');

// Initialize Sequelize instance
// const sequelize = config;

// Models object
const db = {};

// Read all model files and import them
const modelsPath = __dirname;
fs.readdirSync(modelsPath)
  .filter((file) => {
    return (
      file.indexOf('.') !== 0 &&
      file !== 'index.js' &&
      file.slice(-3) === '.js'
    );
  })
  .forEach((file) => {
    const model = require(path.join(modelsPath, file))(sequelize);
    db[model.name] = model;
    logger.info(`Model loaded: ${model.name}`);
  });

// Execute associate methods if they exist
Object.keys(db).forEach((modelName) => {
  if (db[modelName].associate) {
    db[modelName].associate(db);
    logger.info(`Associations created for: ${modelName}`);
  }
});

// Add sequelize instance and Sequelize class to db object
db.sequelize = sequelize;
db.Sequelize = Sequelize;

// Sync database (development only)
if (process.env.NODE_ENV === 'development' && process.env.DB_SYNC === 'true') {
  sequelize.sync({ alter: true }).then(() => {
    logger.info('Database synchronized');
  }).catch((error) => {
    logger.error('Database sync failed:', error);
  });
}

module.exports = db;
