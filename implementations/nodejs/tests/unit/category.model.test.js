const { Category } = require('../../src/models');

describe('Category Model', () => {
  describe('Validation', () => {
    it('should create a valid category', async () => {
      const categoryData = {
        sourcedId: 'cat-test-001',
        status: 'active',
        title: 'Test Category',
        weight: 0.5,
      };

      const category = Category.build(categoryData);
      await expect(category.validate()).resolves.not.toThrow();
    });

    it('should require sourcedId', async () => {
      const categoryData = {
        status: 'active',
        title: 'Test Category',
      };

      const category = Category.build(categoryData);
      await expect(category.validate()).rejects.toThrow();
    });

    it('should require title', async () => {
      const categoryData = {
        sourcedId: 'cat-test-002',
        status: 'active',
      };

      const category = Category.build(categoryData);
      await expect(category.validate()).rejects.toThrow();
    });

    it('should validate weight range (0-1)', async () => {
      const categoryData = {
        sourcedId: 'cat-test-003',
        status: 'active',
        title: 'Test Category',
        weight: 1.5, // Invalid
      };

      const category = Category.build(categoryData);
      await expect(category.validate()).rejects.toThrow();
    });

    it('should validate status enum', async () => {
      const categoryData = {
        sourcedId: 'cat-test-004',
        status: 'invalid_status', // Invalid
        title: 'Test Category',
      };

      const category = Category.build(categoryData);
      await expect(category.validate()).rejects.toThrow();
    });
  });

  describe('toJSON method', () => {
    it('should return OneRoster format', () => {
      const category = Category.build({
        sourcedId: 'cat-test-005',
        status: 'active',
        dateLastModified: new Date('2024-01-01T00:00:00Z'),
        title: 'Test Category',
        weight: 0.75,
        metadata: { key: 'value' },
      });

      const json = category.toJSON();

      expect(json).toHaveProperty('sourcedId', 'cat-test-005');
      expect(json).toHaveProperty('status', 'active');
      expect(json).toHaveProperty('dateLastModified');
      expect(json).toHaveProperty('title', 'Test Category');
      expect(json).toHaveProperty('weight', 0.75);
      expect(json).toHaveProperty('metadata');
    });

    it('should omit null weight', () => {
      const category = Category.build({
        sourcedId: 'cat-test-006',
        status: 'active',
        dateLastModified: new Date(),
        title: 'Test Category',
        weight: null,
      });

      const json = category.toJSON();
      expect(json).not.toHaveProperty('weight');
    });
  });
});
