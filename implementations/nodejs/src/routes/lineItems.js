const express = require('express');
const { body } = require('express-validator');
const lineItemController = require('../controllers/lineItemController');
const { authenticate, requireScope, SCOPES } = require('../middleware/auth');
const { validate, pagination, filter, sort, fields } = require('../middleware/validators');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * Common query middleware for all routes
 */
const queryMiddleware = [pagination, filter, sort, fields];

/**
 * Validation rules for line item creation
 */
const createLineItemValidation = [
  body('sourcedId')
    .notEmpty()
    .withMessage('sourcedId is required')
    .isLength({ max: 255 })
    .withMessage('sourcedId must be 255 characters or less'),
  body('title')
    .notEmpty()
    .withMessage('title is required')
    .isLength({ max: 255 })
    .withMessage('title must be 255 characters or less'),
  body('description')
    .optional()
    .isString()
    .withMessage('description must be a string'),
  body('assignDate')
    .optional()
    .isISO8601()
    .withMessage('assignDate must be a valid ISO 8601 date'),
  body('dueDate')
    .optional()
    .isISO8601()
    .withMessage('dueDate must be a valid ISO 8601 date'),
  body('classSourcedId')
    .notEmpty()
    .withMessage('classSourcedId is required')
    .isLength({ max: 255 })
    .withMessage('classSourcedId must be 255 characters or less'),
  body('categorySourcedId')
    .optional()
    .isLength({ max: 255 })
    .withMessage('categorySourcedId must be 255 characters or less'),
  body('gradingPeriodSourcedId')
    .optional()
    .isLength({ max: 255 })
    .withMessage('gradingPeriodSourcedId must be 255 characters or less'),
  body('resultValueMin')
    .optional()
    .isFloat({ min: 0 })
    .withMessage('resultValueMin must be a non-negative number'),
  body('resultValueMax')
    .notEmpty()
    .withMessage('resultValueMax is required')
    .isFloat({ min: 0 })
    .withMessage('resultValueMax must be a non-negative number'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('metadata must be an object'),
];

/**
 * Validation rules for line item update
 */
const updateLineItemValidation = [
  body('title')
    .optional()
    .trim()
    .notEmpty()
    .withMessage('title cannot be empty')
    .isLength({ max: 255 })
    .withMessage('title must be 255 characters or less'),
  body('description')
    .optional()
    .isString()
    .withMessage('description must be a string'),
  body('assignDate')
    .optional()
    .isISO8601()
    .withMessage('assignDate must be a valid ISO 8601 date'),
  body('dueDate')
    .optional()
    .isISO8601()
    .withMessage('dueDate must be a valid ISO 8601 date'),
  body('categorySourcedId')
    .optional()
    .isLength({ max: 255 })
    .withMessage('categorySourcedId must be 255 characters or less'),
  body('gradingPeriodSourcedId')
    .optional()
    .isLength({ max: 255 })
    .withMessage('gradingPeriodSourcedId must be 255 characters or less'),
  body('resultValueMin')
    .optional()
    .isFloat({ min: 0 })
    .withMessage('resultValueMin must be a non-negative number'),
  body('resultValueMax')
    .optional()
    .isFloat({ min: 0 })
    .withMessage('resultValueMax must be a non-negative number'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('metadata must be an object'),
];

/**
 * GET /lineItems
 * Get all line items
 * Required scope: roster.readonly or roster-core.readonly
 */
router.get(
  '/',
  authenticate(),
  requireScope([SCOPES.ROSTER_READONLY, SCOPES.ROSTER_CORE_READONLY, SCOPES.LINEITEM_READONLY]),
  queryMiddleware,
  asyncHandler(lineItemController.getAllLineItems)
);

/**
 * GET /lineItems/:id
 * Get line item by ID
 * Required scope: roster.readonly or roster-core.readonly or lineitem.readonly
 */
router.get(
  '/:id',
  authenticate(),
  requireScope([SCOPES.ROSTER_READONLY, SCOPES.ROSTER_CORE_READONLY, SCOPES.LINEITEM_READONLY]),
  queryMiddleware,
  asyncHandler(lineItemController.getLineItemById)
);

/**
 * POST /lineItems
 * Create line item
 * Required scope: lineitem (write access)
 */
router.post(
  '/',
  authenticate(),
  requireScope(SCOPES.LINEITEM_WRITE),
  createLineItemValidation,
  validate,
  asyncHandler(lineItemController.createLineItem)
);

/**
 * PUT /lineItems/:id
 * Update line item
 * Required scope: lineitem (write access)
 */
router.put(
  '/:id',
  authenticate(),
  requireScope(SCOPES.LINEITEM_WRITE),
  updateLineItemValidation,
  validate,
  asyncHandler(lineItemController.updateLineItem)
);

/**
 * DELETE /lineItems/:id
 * Delete line item (soft delete)
 * Required scope: lineitem (write access)
 */
router.delete(
  '/:id',
  authenticate(),
  requireScope(SCOPES.LINEITEM_WRITE),
  asyncHandler(lineItemController.deleteLineItem)
);

/**
 * GET /lineItems/:id/results
 * Get results for a line item
 * Required scope: result.readonly or result (write access)
 */
router.get(
  '/:id/results',
  authenticate(),
  requireScope([SCOPES.RESULT_READONLY, SCOPES.RESULT_WRITE]),
  queryMiddleware,
  asyncHandler(lineItemController.getLineItemResults)
);

module.exports = router;
