const { LineItem } = require('../../src/models');

describe('LineItem Model', () => {
  describe('Validation', () => {
    it('should create a valid line item', async () => {
      const lineItemData = {
        sourcedId: 'li-test-001',
        status: 'active',
        title: 'Test Assignment',
        classSourcedId: 'class-001',
        resultValueMin: 0,
        resultValueMax: 100,
      };

      const lineItem = LineItem.build(lineItemData);
      await expect(lineItem.validate()).resolves.not.toThrow();
    });

    it('should require sourcedId', async () => {
      const lineItemData = {
        status: 'active',
        title: 'Test Assignment',
        classSourcedId: 'class-001',
        resultValueMax: 100,
      };

      const lineItem = LineItem.build(lineItemData);
      await expect(lineItem.validate()).rejects.toThrow();
    });

    it('should require title', async () => {
      const lineItemData = {
        sourcedId: 'li-test-002',
        status: 'active',
        classSourcedId: 'class-001',
        resultValueMax: 100,
      };

      const lineItem = LineItem.build(lineItemData);
      await expect(lineItem.validate()).rejects.toThrow();
    });

    it('should require classSourcedId', async () => {
      const lineItemData = {
        sourcedId: 'li-test-003',
        status: 'active',
        title: 'Test Assignment',
        resultValueMax: 100,
      };

      const lineItem = LineItem.build(lineItemData);
      await expect(lineItem.validate()).rejects.toThrow();
    });

    it('should validate resultValueMax > resultValueMin', async () => {
      const lineItemData = {
        sourcedId: 'li-test-004',
        status: 'active',
        title: 'Test Assignment',
        classSourcedId: 'class-001',
        resultValueMin: 100,
        resultValueMax: 50, // Invalid: max < min
      };

      const lineItem = LineItem.build(lineItemData);
      await expect(lineItem.validate()).rejects.toThrow();
    });
  });

  describe('toJSON method', () => {
    it('should return OneRoster format with all fields', () => {
      const lineItem = LineItem.build({
        sourcedId: 'li-test-005',
        status: 'active',
        dateLastModified: new Date('2024-01-01T00:00:00Z'),
        title: 'Math Quiz 1',
        description: 'First quiz',
        assignDate: new Date('2024-01-05'),
        dueDate: new Date('2024-01-12'),
        classSourcedId: 'class-001',
        categorySourcedId: 'cat-001',
        gradingPeriodSourcedId: 'gp-001',
        resultValueMin: 0,
        resultValueMax: 100,
        metadata: { key: 'value' },
      });

      const json = lineItem.toJSON();

      expect(json).toHaveProperty('sourcedId', 'li-test-005');
      expect(json).toHaveProperty('status', 'active');
      expect(json).toHaveProperty('title', 'Math Quiz 1');
      expect(json).toHaveProperty('description', 'First quiz');
      expect(json).toHaveProperty('class');
      expect(json.class).toHaveProperty('sourcedId', 'class-001');
      expect(json).toHaveProperty('category');
      expect(json).toHaveProperty('gradingPeriod');
      expect(json).toHaveProperty('resultValueMin', 0);
      expect(json).toHaveProperty('resultValueMax', 100);
    });

    it('should omit optional fields when null', () => {
      const lineItem = LineItem.build({
        sourcedId: 'li-test-006',
        status: 'active',
        dateLastModified: new Date(),
        title: 'Test Assignment',
        classSourcedId: 'class-001',
        resultValueMin: 0,
        resultValueMax: 100,
      });

      const json = lineItem.toJSON();
      expect(json).not.toHaveProperty('description');
      expect(json).not.toHaveProperty('assignDate');
      expect(json).not.toHaveProperty('dueDate');
      expect(json).not.toHaveProperty('category');
    });
  });
});
