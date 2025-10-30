const express = require('express');
const resultController = require('../controllers/resultController');
const { authenticate, requireScope, SCOPES } = require('../middleware/auth');
const { pagination, filter, sort, fields } = require('../middleware/validators');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * Common query middleware for all routes
 */
const queryMiddleware = [pagination, filter, sort, fields];

/**
 * GET /students/:studentId/results
 * Get all results for a student
 * Required scope: result.readonly or result (write access)
 */
router.get(
  '/:studentId/results',
  authenticate(),
  requireScope([SCOPES.RESULT_READONLY, SCOPES.RESULT_WRITE]),
  queryMiddleware,
  asyncHandler(resultController.getResultsByStudent)
);

module.exports = router;
