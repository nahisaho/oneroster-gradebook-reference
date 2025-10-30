const { Category, LineItem } = require('../models');
const { NotFoundError, ValidationError } = require('../middleware/errorHandler');
const { filtersToWhere } = require('../middleware/validators');
const logger = require('../utils/logger');

/**
 * Category Controller
 * Implements OneRoster Gradebook Service Category endpoints
 */

/**
 * Get all categories
 * GET /categories
 * Supports: pagination, filtering, sorting, field selection
 */
const getAllCategories = async (req, res) => {
  try {
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info('Getting all categories', { limit, offset, where, order });

    const { count, rows } = await Category.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
    });

    // Build response with pagination links
    const baseUrl = `${req.protocol}://${req.get('host')}${req.baseUrl}${req.path}`;
    const totalPages = Math.ceil(count / limit);
    const currentPage = Math.floor(offset / limit) + 1;

    const response = {
      categories: rows.map(c => c.toJSON()),
    };

    // Add pagination metadata (OneRoster extension)
    if (process.env.INCLUDE_PAGINATION_METADATA === 'true') {
      response._meta = {
        totalCount: count,
        limit,
        offset,
        totalPages,
        currentPage,
      };

      // Add pagination links
      response._links = {
        self: `${baseUrl}?limit=${limit}&offset=${offset}`,
      };

      if (offset + limit < count) {
        response._links.next = `${baseUrl}?limit=${limit}&offset=${offset + limit}`;
      }

      if (offset > 0) {
        response._links.prev = `${baseUrl}?limit=${limit}&offset=${Math.max(0, offset - limit)}`;
      }

      response._links.first = `${baseUrl}?limit=${limit}&offset=0`;
      response._links.last = `${baseUrl}?limit=${limit}&offset=${Math.floor((count - 1) / limit) * limit}`;
    }

    logger.info(`Retrieved ${rows.length} categories (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error('Error getting categories:', error);
    throw error;
  }
};

/**
 * Get category by ID
 * GET /categories/:id
 */
const getCategoryById = async (req, res) => {
  try {
    const { id } = req.params;
    const attributes = req.fields || undefined;

    logger.info(`Getting category: ${id}`);

    const category = await Category.findByPk(id, { attributes });

    if (!category) {
      throw new NotFoundError(`Category not found: ${id}`);
    }

    logger.info(`Retrieved category: ${id}`);
    res.json({ category: category.toJSON() });
  } catch (error) {
    logger.error(`Error getting category ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Update category
 * PUT /categories/:id
 * Updates allowed fields: title, weight, metadata
 */
const updateCategory = async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    logger.info(`Updating category: ${id}`, updates);

    // Find category
    const category = await Category.findByPk(id);

    if (!category) {
      throw new NotFoundError(`Category not found: ${id}`);
    }

    // Only allow updating specific fields
    const allowedFields = ['title', 'weight', 'metadata'];
    const updateData = {};

    Object.keys(updates).forEach(key => {
      if (allowedFields.includes(key)) {
        updateData[key] = updates[key];
      }
    });

    // Validate that at least one field is being updated
    if (Object.keys(updateData).length === 0) {
      throw new ValidationError('No valid fields to update');
    }

    // Update category
    await category.update(updateData);

    logger.info(`Updated category: ${id}`);
    res.json({ category: category.toJSON() });
  } catch (error) {
    logger.error(`Error updating category ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Delete category (soft delete - set status to 'tobedeleted')
 * DELETE /categories/:id
 */
const deleteCategory = async (req, res) => {
  try {
    const { id } = req.params;

    logger.info(`Deleting category: ${id}`);

    const category = await Category.findByPk(id);

    if (!category) {
      throw new NotFoundError(`Category not found: ${id}`);
    }

    // Check if category has line items
    const lineItemCount = await LineItem.count({
      where: { categorySourcedId: id },
    });

    if (lineItemCount > 0) {
      logger.warn(`Category ${id} has ${lineItemCount} line items`);
      
      // Soft delete - set status to 'tobedeleted'
      await category.update({ status: 'tobedeleted' });
      
      logger.info(`Soft deleted category: ${id}`);
      return res.json({
        category: category.toJSON(),
        message: `Category marked as 'tobedeleted' (has ${lineItemCount} associated line items)`,
      });
    }

    // Hard delete if no line items
    await category.destroy();

    logger.info(`Hard deleted category: ${id}`);
    res.status(204).send();
  } catch (error) {
    logger.error(`Error deleting category ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Get line items for a category
 * GET /categories/:id/lineItems
 */
const getCategoryLineItems = async (req, res) => {
  try {
    const { id } = req.params;
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info(`Getting line items for category: ${id}`);

    // Check if category exists
    const category = await Category.findByPk(id);
    if (!category) {
      throw new NotFoundError(`Category not found: ${id}`);
    }

    // Add category filter
    where.categorySourcedId = id;

    const { count, rows } = await LineItem.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
    });

    const response = {
      lineItems: rows.map(li => li.toJSON()),
    };

    // Add pagination metadata
    if (process.env.INCLUDE_PAGINATION_METADATA === 'true') {
      response._meta = {
        totalCount: count,
        limit,
        offset,
      };
    }

    logger.info(`Retrieved ${rows.length} line items for category ${id} (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error(`Error getting line items for category ${req.params.id}:`, error);
    throw error;
  }
};

module.exports = {
  getAllCategories,
  getCategoryById,
  updateCategory,
  deleteCategory,
  getCategoryLineItems,
};
