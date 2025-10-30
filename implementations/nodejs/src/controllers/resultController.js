const { Result, LineItem } = require('../models');
const { NotFoundError, ValidationError } = require('../middleware/errorHandler');
const { filtersToWhere } = require('../middleware/validators');
const logger = require('../utils/logger');

/**
 * Result Controller
 * Implements OneRoster Gradebook Service Result endpoints
 */

/**
 * Get all results
 * GET /results
 * Supports: pagination, filtering, sorting, field selection
 */
const getAllResults = async (req, res) => {
  try {
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info('Getting all results', { limit, offset, where, order });

    const { count, rows } = await Result.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
      include: req.query.include === 'lineItem' ? [
        { model: LineItem, as: 'lineItem', attributes: ['sourcedId', 'title'] }
      ] : undefined,
    });

    // Build response
    const baseUrl = `${req.protocol}://${req.get('host')}${req.baseUrl}${req.path}`;
    const response = {
      results: rows.map(r => r.toJSON()),
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

    logger.info(`Retrieved ${rows.length} results (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error('Error getting results:', error);
    throw error;
  }
};

/**
 * Get result by ID
 * GET /results/:id
 */
const getResultById = async (req, res) => {
  try {
    const { id } = req.params;
    const attributes = req.fields || undefined;

    logger.info(`Getting result: ${id}`);

    const result = await Result.findByPk(id, {
      attributes,
      include: req.query.include === 'lineItem' ? [
        { model: LineItem, as: 'lineItem', attributes: ['sourcedId', 'title'] }
      ] : undefined,
    });

    if (!result) {
      throw new NotFoundError(`Result not found: ${id}`);
    }

    logger.info(`Retrieved result: ${id}`);
    res.json({ result: result.toJSON() });
  } catch (error) {
    logger.error(`Error getting result ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Create result
 * POST /results
 */
const createResult = async (req, res) => {
  try {
    const data = req.body;

    logger.info('Creating result', data);

    // Validate required fields
    const requiredFields = ['sourcedId', 'lineItemSourcedId', 'studentSourcedId', 'scoreStatus'];
    const missingFields = requiredFields.filter(field => !data[field]);

    if (missingFields.length > 0) {
      throw new ValidationError(`Missing required fields: ${missingFields.join(', ')}`);
    }

    // Validate line item exists
    const lineItem = await LineItem.findByPk(data.lineItemSourcedId);
    if (!lineItem) {
      throw new ValidationError(`LineItem not found: ${data.lineItemSourcedId}`);
    }

    // Validate score requirements based on scoreStatus
    const requireScore = ['fully graded', 'partially graded'];
    const noScore = ['exempt', 'not submitted'];

    if (requireScore.includes(data.scoreStatus) && (data.score === null || data.score === undefined)) {
      throw new ValidationError(`score is required when scoreStatus is '${data.scoreStatus}'`);
    }

    if (noScore.includes(data.scoreStatus) && data.score !== null && data.score !== undefined) {
      throw new ValidationError(`score must be null when scoreStatus is '${data.scoreStatus}'`);
    }

    // Create result
    const result = await Result.create(data);

    logger.info(`Created result: ${result.sourcedId}`);
    res.status(201).json({ result: result.toJSON() });
  } catch (error) {
    logger.error('Error creating result:', error);
    throw error;
  }
};

/**
 * Update result
 * PUT /results/:id
 */
const updateResult = async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    logger.info(`Updating result: ${id}`, updates);

    // Find result
    const result = await Result.findByPk(id);

    if (!result) {
      throw new NotFoundError(`Result not found: ${id}`);
    }

    // Only allow updating specific fields
    const allowedFields = ['scoreStatus', 'score', 'scoreDate', 'comment', 'metadata'];
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

    // Validate score requirements if scoreStatus is being updated
    if (updateData.scoreStatus) {
      const requireScore = ['fully graded', 'partially graded'];
      const noScore = ['exempt', 'not submitted'];
      
      const finalScore = updateData.score !== undefined ? updateData.score : result.score;

      if (requireScore.includes(updateData.scoreStatus) && (finalScore === null || finalScore === undefined)) {
        throw new ValidationError(`score is required when scoreStatus is '${updateData.scoreStatus}'`);
      }

      if (noScore.includes(updateData.scoreStatus) && finalScore !== null && finalScore !== undefined) {
        throw new ValidationError(`score must be null when scoreStatus is '${updateData.scoreStatus}'`);
      }
    }

    // Update result
    await result.update(updateData);

    logger.info(`Updated result: ${id}`);
    res.json({ result: result.toJSON() });
  } catch (error) {
    logger.error(`Error updating result ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Delete result
 * DELETE /results/:id
 */
const deleteResult = async (req, res) => {
  try {
    const { id } = req.params;

    logger.info(`Deleting result: ${id}`);

    const result = await Result.findByPk(id);

    if (!result) {
      throw new NotFoundError(`Result not found: ${id}`);
    }

    // Hard delete result
    await result.destroy();

    logger.info(`Deleted result: ${id}`);
    res.status(204).send();
  } catch (error) {
    logger.error(`Error deleting result ${req.params.id}:`, error);
    throw error;
  }
};

/**
 * Get results by student
 * GET /students/:studentId/results
 */
const getResultsByStudent = async (req, res) => {
  try {
    const { studentId } = req.params;
    const { limit, offset } = req.pagination;
    const where = req.filters ? filtersToWhere(req.filters) : {};
    const order = req.sort || [['dateLastModified', 'DESC']];
    const attributes = req.fields || undefined;

    logger.info(`Getting results for student: ${studentId}`);

    // Add student filter
    where.studentSourcedId = studentId;

    const { count, rows } = await Result.findAndCountAll({
      where,
      limit,
      offset,
      order,
      attributes,
      include: req.query.include === 'lineItem' ? [
        { model: LineItem, as: 'lineItem', attributes: ['sourcedId', 'title', 'classSourcedId'] }
      ] : undefined,
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

    logger.info(`Retrieved ${rows.length} results for student ${studentId} (total: ${count})`);
    res.json(response);
  } catch (error) {
    logger.error(`Error getting results for student ${req.params.studentId}:`, error);
    throw error;
  }
};

module.exports = {
  getAllResults,
  getResultById,
  createResult,
  updateResult,
  deleteResult,
  getResultsByStudent,
};
