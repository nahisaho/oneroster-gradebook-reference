const { filtersToWhere } = require('../../src/middleware/validators');
const { Op } = require('sequelize');

describe('Validators Middleware', () => {
  describe('filtersToWhere', () => {
    it('should convert == operator to equality', () => {
      const filters = {
        status: [{ operator: '==', value: 'active' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ status: 'active' });
    });

    it('should convert != operator to not equal', () => {
      const filters = {
        status: [{ operator: '!=', value: 'tobedeleted' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ status: { [Op.ne]: 'tobedeleted' } });
    });

    it('should convert > operator to greater than', () => {
      const filters = {
        score: [{ operator: '>', value: '80' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ score: { [Op.gt]: '80' } });
    });

    it('should convert < operator to less than', () => {
      const filters = {
        score: [{ operator: '<', value: '50' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ score: { [Op.lt]: '50' } });
    });

    it('should convert >= operator to greater than or equal', () => {
      const filters = {
        weight: [{ operator: '>=', value: '0.5' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ weight: { [Op.gte]: '0.5' } });
    });

    it('should convert <= operator to less than or equal', () => {
      const filters = {
        weight: [{ operator: '<=', value: '1.0' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ weight: { [Op.lte]: '1.0' } });
    });

    it('should convert ~ operator to LIKE', () => {
      const filters = {
        title: [{ operator: '~', value: 'Math' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toEqual({ title: { [Op.like]: '%Math%' } });
    });

    it('should handle multiple conditions with AND', () => {
      const filters = {
        score: [
          { operator: '>=', value: '70' },
          { operator: '<=', value: '90' },
        ],
      };

      const where = filtersToWhere(filters);
      expect(where[Op.and]).toHaveLength(2);
    });

    it('should handle multiple fields', () => {
      const filters = {
        status: [{ operator: '==', value: 'active' }],
        title: [{ operator: '~', value: 'Quiz' }],
      };

      const where = filtersToWhere(filters);
      expect(where).toHaveProperty('status', 'active');
      expect(where).toHaveProperty('title');
    });
  });
});
