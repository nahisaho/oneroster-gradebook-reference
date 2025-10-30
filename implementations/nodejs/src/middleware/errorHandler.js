const logger = require('../utils/logger');

/**
 * OneRoster error response format
 * @param {Object} res - Express response object
 * @param {number} statusCode - HTTP status code
 * @param {string} description - Error description
 * @param {string} codeMinor - Error code minor
 */
const sendOneRosterError = (res, statusCode, description, codeMinor) => {
  const imsx_codeMajor = statusCode >= 200 && statusCode < 300 ? 'success' : 'failure';
  const imsx_severity = statusCode >= 400 ? 'error' : 'warning';

  res.status(statusCode).json({
    imsx_codeMajor,
    imsx_severity,
    imsx_description: description,
    imsx_codeMinor: codeMinor,
  });
};

/**
 * Not Found handler
 * Returns OneRoster formatted 404 error
 */
const notFound = (req, res, next) => {
  logger.warn(`404 Not Found: ${req.method} ${req.path}`);
  
  sendOneRosterError(
    res,
    404,
    `Resource not found: ${req.path}`,
    'not_found'
  );
};

/**
 * Global error handler
 * Catches all errors and returns OneRoster formatted response
 */
const errorHandler = (err, req, res, next) => {
  // Log error
  logger.error('Error:', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  // Determine status code
  let statusCode = err.statusCode || err.status || 500;
  let description = err.message || 'Internal server error';
  let codeMinor = 'server_error';

  // Handle specific error types
  if (err.name === 'ValidationError') {
    statusCode = 400;
    codeMinor = 'invalid_data';
    
    // Extract validation errors
    if (err.errors) {
      const messages = Object.values(err.errors).map(e => e.message);
      description = `Validation error: ${messages.join(', ')}`;
    }
  } else if (err.name === 'SequelizeValidationError') {
    statusCode = 400;
    codeMinor = 'invalid_data';
    
    if (err.errors) {
      const messages = err.errors.map(e => `${e.path}: ${e.message}`);
      description = `Validation error: ${messages.join(', ')}`;
    }
  } else if (err.name === 'SequelizeUniqueConstraintError') {
    statusCode = 409;
    codeMinor = 'conflict';
    description = 'Resource already exists';
  } else if (err.name === 'SequelizeForeignKeyConstraintError') {
    statusCode = 400;
    codeMinor = 'invalid_data';
    description = 'Invalid reference to related resource';
  } else if (err.name === 'SequelizeDatabaseError') {
    statusCode = 500;
    codeMinor = 'server_error';
    description = 'Database error';
  } else if (err.name === 'UnauthorizedError' || err.name === 'OAuthError') {
    statusCode = 401;
    codeMinor = 'unauthorized';
    description = err.message || 'Unauthorized';
  } else if (err.name === 'ForbiddenError') {
    statusCode = 403;
    codeMinor = 'forbidden';
    description = err.message || 'Forbidden';
  }

  // Don't expose internal errors in production
  if (statusCode === 500 && process.env.NODE_ENV === 'production') {
    description = 'Internal server error';
  }

  sendOneRosterError(res, statusCode, description, codeMinor);
};

/**
 * Async error wrapper
 * Wraps async route handlers to catch errors
 * @param {Function} fn - Async function
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * Custom error classes
 */
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 400;
  }
}

class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

class UnauthorizedError extends Error {
  constructor(message = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
    this.statusCode = 401;
  }
}

class ForbiddenError extends Error {
  constructor(message = 'Forbidden') {
    super(message);
    this.name = 'ForbiddenError';
    this.statusCode = 403;
  }
}

class ConflictError extends Error {
  constructor(message = 'Resource conflict') {
    super(message);
    this.name = 'ConflictError';
    this.statusCode = 409;
  }
}

module.exports = {
  sendOneRosterError,
  notFound,
  errorHandler,
  asyncHandler,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
};
