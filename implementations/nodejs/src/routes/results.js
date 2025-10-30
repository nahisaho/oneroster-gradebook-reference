const express = require('express');
const { body } = require('express-validator');
const resultController = require('../controllers/resultController');
const { authenticate, requireScope, SCOPES } = require('../middleware/auth');
const { validate, pagination, filter, sort, fields } = require('../middleware/validators');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * Common query middleware for all routes
 */
const queryMiddleware = [pagination, filter, sort, fields];

/**
 * Validation rules for result creation
 */
const createResultValidation = [
  body('sourcedId')
    .notEmpty()
    .withMessage('sourcedId is required')
    .isLength({ max: 255 })
    .withMessage('sourcedId must be 255 characters or less'),
  body('lineItemSourcedId')
    .notEmpty()
    .withMessage('lineItemSourcedId is required')
    .isLength({ max: 255 })
    .withMessage('lineItemSourcedId must be 255 characters or less'),
  body('studentSourcedId')
    .notEmpty()
    .withMessage('studentSourcedId is required')
    .isLength({ max: 255 })
    .withMessage('studentSourcedId must be 255 characters or less'),
  body('scoreStatus')
    .notEmpty()
    .withMessage('scoreStatus is required')
    .isIn(['exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted'])
    .withMessage('scoreStatus must be one of: exempt, fully graded, not submitted, partially graded, submitted'),
  body('score')
    .optional()
    .isFloat()
    .withMessage('score must be a number'),
  body('scoreDate')
    .optional()
    .isISO8601()
    .withMessage('scoreDate must be a valid ISO 8601 date'),
  body('comment')
    .optional()
    .isString()
    .withMessage('comment must be a string'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('metadata must be an object'),
];

/**
 * Validation rules for result update
 */
const updateResultValidation = [
  body('scoreStatus')
    .optional()
    .isIn(['exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted'])
    .withMessage('scoreStatus must be one of: exempt, fully graded, not submitted, partially graded, submitted'),
  body('score')
    .optional()
    .isFloat()
    .withMessage('score must be a number'),
  body('scoreDate')
    .optional()
    .isISO8601()
    .withMessage('scoreDate must be a valid ISO 8601 date'),
  body('comment')
    .optional()
    .isString()
    .withMessage('comment must be a string'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('metadata must be an object'),
];

/**
 * GET /results
 * Get all results
 * Required scope: result.readonly or result (write access)
 */
router.get(
  '/',
  authenticate(),
  requireScope([SCOPES.RESULT_READONLY, SCOPES.RESULT_WRITE]),
  queryMiddleware,
  asyncHandler(resultController.getAllResults)
);

/**
 * GET /results/:id
 * Get result by ID
 * Required scope: result.readonly or result (write access)
 */
router.get(
  '/:id',
  authenticate(),
  requireScope([SCOPES.RESULT_READONLY, SCOPES.RESULT_WRITE]),
  queryMiddleware,
  asyncHandler(resultController.getResultById)
);

/**
 * POST /results
 * Create result
 * Required scope: result (write access)
 */
router.post(
  '/',
  authenticate(),
  requireScope(SCOPES.RESULT_WRITE),
  createResultValidation,
  validate,
  asyncHandler(resultController.createResult)
);

/**
 * PUT /results/:id
 * Update result
 * Required scope: result (write access)
 */
router.put(
  '/:id',
  authenticate(),
  requireScope(SCOPES.RESULT_WRITE),
  updateResultValidation,
  validate,
  asyncHandler(resultController.updateResult)
);

/**
 * DELETE /results/:id
 * Delete result
 * Required scope: result (write access)
 */
router.delete(
  '/:id',
  authenticate(),
  requireScope(SCOPES.RESULT_WRITE),
  asyncHandler(resultController.deleteResult)
);

module.exports = router;
