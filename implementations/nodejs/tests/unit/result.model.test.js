const { Result } = require('../../src/models');

describe('Result Model', () => {
  describe('Validation', () => {
    it('should create a valid result', async () => {
      const resultData = {
        sourcedId: 'res-test-001',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'fully graded',
        score: 85.5,
      };

      const result = Result.build(resultData);
      await expect(result.validate()).resolves.not.toThrow();
    });

    it('should require sourcedId', async () => {
      const resultData = {
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'submitted',
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should require lineItemSourcedId', async () => {
      const resultData = {
        sourcedId: 'res-test-002',
        status: 'active',
        studentSourcedId: 'student-001',
        scoreStatus: 'submitted',
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should require studentSourcedId', async () => {
      const resultData = {
        sourcedId: 'res-test-003',
        status: 'active',
        lineItemSourcedId: 'li-001',
        scoreStatus: 'submitted',
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should require scoreStatus', async () => {
      const resultData = {
        sourcedId: 'res-test-004',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should validate scoreStatus enum', async () => {
      const resultData = {
        sourcedId: 'res-test-005',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'invalid_status', // Invalid
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should require score for "fully graded" status', async () => {
      const resultData = {
        sourcedId: 'res-test-006',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'fully graded',
        score: null, // Invalid: score required
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should require score for "partially graded" status', async () => {
      const resultData = {
        sourcedId: 'res-test-007',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'partially graded',
        score: null, // Invalid: score required
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should not allow score for "exempt" status', async () => {
      const resultData = {
        sourcedId: 'res-test-008',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'exempt',
        score: 85, // Invalid: score not allowed
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });

    it('should not allow score for "not submitted" status', async () => {
      const resultData = {
        sourcedId: 'res-test-009',
        status: 'active',
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'not submitted',
        score: 85, // Invalid: score not allowed
      };

      const result = Result.build(resultData);
      await expect(result.validate()).rejects.toThrow();
    });
  });

  describe('toJSON method', () => {
    it('should return OneRoster format with all fields', () => {
      const result = Result.build({
        sourcedId: 'res-test-010',
        status: 'active',
        dateLastModified: new Date('2024-01-01T00:00:00Z'),
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'fully graded',
        score: 92.5,
        scoreDate: new Date('2024-01-15T10:00:00Z'),
        comment: 'Excellent work!',
        metadata: { key: 'value' },
      });

      const json = result.toJSON();

      expect(json).toHaveProperty('sourcedId', 'res-test-010');
      expect(json).toHaveProperty('status', 'active');
      expect(json).toHaveProperty('lineItem');
      expect(json.lineItem).toHaveProperty('sourcedId', 'li-001');
      expect(json).toHaveProperty('student');
      expect(json.student).toHaveProperty('sourcedId', 'student-001');
      expect(json).toHaveProperty('scoreStatus', 'fully graded');
      expect(json).toHaveProperty('score', 92.5);
      expect(json).toHaveProperty('scoreDate');
      expect(json).toHaveProperty('comment', 'Excellent work!');
      expect(json).toHaveProperty('metadata');
    });

    it('should omit null score', () => {
      const result = Result.build({
        sourcedId: 'res-test-011',
        status: 'active',
        dateLastModified: new Date(),
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'exempt',
        score: null,
      });

      const json = result.toJSON();
      expect(json).not.toHaveProperty('score');
    });

    it('should omit optional fields when null', () => {
      const result = Result.build({
        sourcedId: 'res-test-012',
        status: 'active',
        dateLastModified: new Date(),
        lineItemSourcedId: 'li-001',
        studentSourcedId: 'student-001',
        scoreStatus: 'submitted',
      });

      const json = result.toJSON();
      expect(json).not.toHaveProperty('score');
      expect(json).not.toHaveProperty('scoreDate');
      expect(json).not.toHaveProperty('comment');
    });
  });
});
