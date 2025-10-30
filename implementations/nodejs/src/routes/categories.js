const express = require('express');
const { body } = require('express-validator');
const categoryController = require('../controllers/categoryController');
const { authenticate, requireScope, SCOPES } = require('../middleware/auth');
const { validate, pagination, filter, sort, fields } = require('../middleware/validators');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * Common query middleware for all routes
 */
const queryMiddleware = [pagination, filter, sort, fields];

/**
 * Validation rules for category
 */
const categoryValidation = [
  body('title')
    .optional()
    .trim()
    .notEmpty()
    .withMessage('title cannot be empty')
    .isLength({ max: 255 })
    .withMessage('title must be 255 characters or less'),
  body('weight')
    .optional()
    .isFloat({ min: 0.0, max: 1.0 })
    .withMessage('weight must be between 0.0 and 1.0'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('metadata must be an object'),
];

/**
 * GET /categories
 * Get all categories
 * Required scope: roster.readonly or roster-core.readonly
 */
router.get(
  '/',
  authenticate(),
  requireScope([SCOPES.ROSTER_READONLY, SCOPES.ROSTER_CORE_READONLY]),
  queryMiddleware,
  asyncHandler(categoryController.getAllCategories)
);

/**
 * GET /categories/:id
 * Get category by ID
 * Required scope: roster.readonly or roster-core.readonly
 */
router.get(
  '/:id',
  authenticate(),
  requireScope([SCOPES.ROSTER_READONLY, SCOPES.ROSTER_CORE_READONLY]),
  queryMiddleware,
  asyncHandler(categoryController.getCategoryById)
);

/**
 * PUT /categories/:id
 * Update category
 * Required scope: lineitem (write access)
 */
router.put(
  '/:id',
  authenticate(),
  requireScope(SCOPES.LINEITEM_WRITE),
  categoryValidation,
  validate,
  asyncHandler(categoryController.updateCategory)
);

/**
 * DELETE /categories/:id
 * Delete category (soft delete)
 * Required scope: lineitem (write access)
 */
router.delete(
  '/:id',
  authenticate(),
  requireScope(SCOPES.LINEITEM_WRITE),
  asyncHandler(categoryController.deleteCategory)
);

/**
 * GET /categories/:id/lineItems
 * Get line items for a category
 * Required scope: roster.readonly or roster-core.readonly
 */
router.get(
  '/:id/lineItems',
  authenticate(),
  requireScope([SCOPES.ROSTER_READONLY, SCOPES.ROSTER_CORE_READONLY]),
  queryMiddleware,
  asyncHandler(categoryController.getCategoryLineItems)
);

module.exports = router;
