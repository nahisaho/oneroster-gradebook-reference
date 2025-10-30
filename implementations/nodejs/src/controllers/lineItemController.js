const { LineItem, Category, Result } = require('../models');
const { NotFoundError, ValidationError } = require('../middleware/errorHandler');
const { filtersToWhere } = require('../middleware/validators');
const logger = require('../utils/logger');

/**
 * LineItem Controller
 * Implements OneRoster Gradebook Service LineItem endpoints
 */

/**
 * Get all line items
 * GET /lineItems
 * Supports: pagination, filtering, sorting, field selection
 */
const getAllLineItems = async (req, res) => {
  try {
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info('Getting all line items', { limit, offset, where, order });

    const { count, rows } = await LineItem.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
      include: req.query.include === 'category' ? [
        { model: Category, as: 'category', attributes: ['sourcedId', 'title'] }
      ] : undefined,
    });

    // Build response
    const baseUrl = `${req.protocol}://${req.get('host')}${req.baseUrl}${req.path}`;
    const response = {
      lineItems: rows.map(li => li.toJSON()),
    };

    // Add pagination metadata
    if (process.env.INCLUDE_PAGINATION_METADATA === 'true') {
      const totalPages = Math.ceil(count / limit);
      const currentPage = Math.floor(offset / limit) + 1;

      response._meta = {
        totalCount: count,
        limit,
        offset,
        totalPages,
        currentPage,
      };

      response._links = {
        self: `${baseUrl}?limit=${limit}&offset=${offset}`,
      };

      if (offset + limit < count) {
        response._links.next = `${baseUrl}?limit=${limit}&offset=${offset + limit}`;
      }

      if (offset > 0) {
        response._links.prev = `${baseUrl}?limit=${limit}&offset=${Math.max(0, offset - limit)}`;
      }
    }

    logger.info(`Retrieved ${rows.length} line items (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error('Error getting line items:', error);
    throw error;
  }
};

/**
 * Get line item by ID
 * GET /lineItems/:id
 */
const getLineItemById = async (req, res) => {
  try {
    const { id } = req.params;
    const attributes = req.fields || undefined;

    logger.info(`Getting line item: ${id}`);

    const lineItem = await LineItem.findByPk(id, {
      attributes,
      include: req.query.include === 'category' ? [
        { model: Category, as: 'category', attributes: ['sourcedId', 'title'] }
      ] : undefined,
    });

    if (!lineItem) {
      throw new NotFoundError(`LineItem not found: ${id}`);
    }

    logger.info(`Retrieved line item: ${id}`);
    res.json({ lineItem: lineItem.toJSON() });
  } catch (error) {
    logger.error(`Error getting line item ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Create line item
 * POST /lineItems
 */
const createLineItem = async (req, res) => {
  try {
    const data = req.body;

    logger.info('Creating line item', data);

    // Validate required fields
    const requiredFields = ['sourcedId', 'title', 'classSourcedId', 'resultValueMax'];
    const missingFields = requiredFields.filter(field => !data[field]);

    if (missingFields.length > 0) {
      throw new ValidationError(`Missing required fields: ${missingFields.join(', ')}`);
    }

    // Validate category exists if provided
    if (data.categorySourcedId) {
      const category = await Category.findByPk(data.categorySourcedId);
      if (!category) {
        throw new ValidationError(`Category not found: ${data.categorySourcedId}`);
      }
    }

    // Create line item
    const lineItem = await LineItem.create(data);

    logger.info(`Created line item: ${lineItem.sourcedId}`);
    res.status(201).json({ lineItem: lineItem.toJSON() });
  } catch (error) {
    logger.error('Error creating line item:', error);
    throw error;
  }
};

/**
 * Update line item
 * PUT /lineItems/:id
 */
const updateLineItem = async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    logger.info(`Updating line item: ${id}`, updates);

    // Find line item
    const lineItem = await LineItem.findByPk(id);

    if (!lineItem) {
      throw new NotFoundError(`LineItem not found: ${id}`);
    }

    // Only allow updating specific fields
    const allowedFields = [
      'title', 'description', 'assignDate', 'dueDate',
      'categorySourcedId', 'gradingPeriodSourcedId',
      'resultValueMin', 'resultValueMax', 'metadata'
    ];
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

    // Validate category exists if being updated
    if (updateData.categorySourcedId) {
      const category = await Category.findByPk(updateData.categorySourcedId);
      if (!category) {
        throw new ValidationError(`Category not found: ${updateData.categorySourcedId}`);
      }
    }

    // Update line item
    await lineItem.update(updateData);

    logger.info(`Updated line item: ${id}`);
    res.json({ lineItem: lineItem.toJSON() });
  } catch (error) {
    logger.error(`Error updating line item ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Delete line item (soft delete - set status to 'tobedeleted')
 * DELETE /lineItems/:id
 */
const deleteLineItem = async (req, res) => {
  try {
    const { id } = req.params;

    logger.info(`Deleting line item: ${id}`);

    const lineItem = await LineItem.findByPk(id);

    if (!lineItem) {
      throw new NotFoundError(`LineItem not found: ${id}`);
    }

    // Check if line item has results
    const resultCount = await Result.count({
      where: { lineItemSourcedId: id },
    });

    if (resultCount > 0) {
      logger.warn(`LineItem ${id} has ${resultCount} results`);
      
      // Soft delete - set status to 'tobedeleted'
      await lineItem.update({ status: 'tobedeleted' });
      
      logger.info(`Soft deleted line item: ${id}`);
      return res.json({
        lineItem: lineItem.toJSON(),
        message: `LineItem marked as 'tobedeleted' (has ${resultCount} associated results)`,
      });
    }

    // Hard delete if no results
    await lineItem.destroy();

    logger.info(`Hard deleted line item: ${id}`);
    res.status(204).send();
  } catch (error) {
    logger.error(`Error deleting line item ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Get results for a line item
 * GET /lineItems/:id/results
 */
const getLineItemResults = async (req, res) => {
  try {
    const { id } = req.params;
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info(`Getting results for line item: ${id}`);

    // Check if line item exists
    const lineItem = await LineItem.findByPk(id);
    if (!lineItem) {
      throw new NotFoundError(`LineItem not found: ${id}`);
    }

    // Add line item filter
    where.lineItemSourcedId = id;

    const { count, rows } = await Result.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
    });

    const response = {
      results: rows.map(r => r.toJSON()),
    };

    // Add pagination metadata
    if (process.env.INCLUDE_PAGINATION_METADATA === 'true') {
      response._meta = {
        totalCount: count,
        limit,
        offset,
      };
    }

    logger.info(`Retrieved ${rows.length} results for line item ${id} (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error(`Error getting results for line item ${req.params.id}:`, error);
    throw error;
  }
};

module.exports = {
  getAllLineItems,
  getLineItemById,
  createLineItem,
  updateLineItem,
  deleteLineItem,
  getLineItemResults,
};
