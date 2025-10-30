const { validationResult } = require('express-validator');
const { ValidationError } = require('./errorHandler');

/**
 * Validate request using express-validator
 * Throws ValidationError if validation fails
 */
const validate = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    const messages = errors.array().map(err => {
      if (err.nestedErrors) {
        return err.nestedErrors.map(e => `${e.param}: ${e.msg}`).join(', ');
      }
      return `${err.param}: ${err.msg}`;
    });
    
    throw new ValidationError(messages.join('; '));
  }
  
  next();
};

/**
 * Pagination middleware
 * Extracts and validates limit and offset query parameters
 * Sets defaults: limit=100, offset=0
 */
const pagination = (req, res, next) => {
  // Get limit and offset from query parameters
  let limit = parseInt(req.query.limit, 10);
  let offset = parseInt(req.query.offset, 10);

  // Set defaults
  if (isNaN(limit) || limit <= 0) {
    limit = 100;
  }
  if (isNaN(offset) || offset < 0) {
    offset = 0;
  }

  // Apply max limit
  const maxLimit = parseInt(process.env.MAX_PAGE_SIZE || '500', 10);
  if (limit > maxLimit) {
    limit = maxLimit;
  }

  // Attach to request
  req.pagination = {
    limit,
    offset,
  };

  next();
};

/**
 * Filter middleware
 * Parses filter query parameter
 * Format: ?filter=field==value,field2!=value2
 */
const filter = (req, res, next) => {
  const filterString = req.query.filter;
  const filters = {};

  if (!filterString) {
    req.filters = filters;
    return next();
  }

  try {
    // Split by comma to get individual filters
    const filterPairs = filterString.split(',');

    filterPairs.forEach(pair => {
      // Match operators: ==, !=, >, <, >=, <=, ~
      const match = pair.match(/^([^=!><~]+)(==|!=|>=|<=|>|<|~)(.+)$/);
      
      if (!match) {
        throw new ValidationError(`Invalid filter format: ${pair}`);
      }

      const [, field, operator, value] = match;
      const trimmedField = field.trim();
      const trimmedValue = value.trim();

      // Initialize field filter
      if (!filters[trimmedField]) {
        filters[trimmedField] = [];
      }

      // Add filter condition
      filters[trimmedField].push({
        operator,
        value: trimmedValue,
      });
    });

    req.filters = filters;
    next();
  } catch (error) {
    throw new ValidationError(`Invalid filter parameter: ${error.message}`);
  }
};

/**
 * Sort middleware
 * Parses sort query parameter
 * Format: ?sort=field or ?sort=-field (descending)
 */
const sort = (req, res, next) => {
  const sortString = req.query.sort;
  const sort = [];

  if (!sortString) {
    // Default sort by dateLastModified descending
    req.sort = [['dateLastModified', 'DESC']];
    return next();
  }

  try {
    // Split by comma for multiple sort fields
    const sortFields = sortString.split(',');

    sortFields.forEach(field => {
      const trimmedField = field.trim();
      
      if (trimmedField.startsWith('-')) {
        // Descending
        sort.push([trimmedField.substring(1), 'DESC']);
      } else {
        // Ascending
        sort.push([trimmedField, 'ASC']);
      }
    });

    req.sort = sort;
    next();
  } catch (error) {
    throw new ValidationError(`Invalid sort parameter: ${error.message}`);
  }
};

/**
 * Field selection middleware
 * Parses fields query parameter
 * Format: ?fields=field1,field2,field3
 */
const fields = (req, res, next) => {
  const fieldsString = req.query.fields;
  
  if (!fieldsString) {
    req.fields = null; // Return all fields
    return next();
  }

  try {
    // Split by comma and trim
    const fieldList = fieldsString.split(',').map(f => f.trim());
    
    // Always include required OneRoster fields
    const requiredFields = ['sourcedId', 'status', 'dateLastModified'];
    const uniqueFields = [...new Set([...requiredFields, ...fieldList])];
    
    req.fields = uniqueFields;
    next();
  } catch (error) {
    throw new ValidationError(`Invalid fields parameter: ${error.message}`);
  }
};

/**
 * Convert filter conditions to Sequelize where clause
 * @param {Object} filters - Parsed filters from filter middleware
 * @returns {Object} Sequelize where clause
 */
const filtersToWhere = (filters) => {
  const { Op } = require('sequelize');
  const where = {};

  Object.keys(filters).forEach(field => {
    const conditions = filters[field];
    
    if (conditions.length === 1) {
      // Single condition
      const { operator, value } = conditions[0];
      
      switch (operator) {
        case '==':
          where[field] = value;
          break;
        case '!=':
          where[field] = { [Op.ne]: value };
          break;
        case '>':
          where[field] = { [Op.gt]: value };
          break;
        case '<':
          where[field] = { [Op.lt]: value };
          break;
        case '>=':
          where[field] = { [Op.gte]: value };
          break;
        case '<=':
          where[field] = { [Op.lte]: value };
          break;
        case '~':
          where[field] = { [Op.like]: `%${value}%` };
          break;
      }
    } else {
      // Multiple conditions - combine with AND
      const andConditions = conditions.map(({ operator, value }) => {
        switch (operator) {
          case '==':
            return { [field]: value };
          case '!=':
            return { [field]: { [Op.ne]: value } };
          case '>':
            return { [field]: { [Op.gt]: value } };
          case '<':
            return { [field]: { [Op.lt]: value } };
          case '>=':
            return { [field]: { [Op.gte]: value } };
          case '<=':
            return { [field]: { [Op.lte]: value } };
          case '~':
            return { [field]: { [Op.like]: `%${value}%` } };
          default:
            return {};
        }
      });
      
      where[Op.and] = [...(where[Op.and] || []), ...andConditions];
    }
  });

  return where;
};

module.exports = {
  validate,
  pagination,
  filter,
  sort,
  fields,
  filtersToWhere,
};
