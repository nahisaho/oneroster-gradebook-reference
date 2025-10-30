const request = require('supertest');
const app = require('../../src/app');
const db = require('../../src/models');

describe('Health Check', () => {
  afterAll(async () => {
    await db.sequelize.close();
  });

  it('should return health status', async () => {
    const res = await request(app)
      .get('/health')
      .expect(200);

    expect(res.body).toHaveProperty('status', 'ok');
    expect(res.body).toHaveProperty('timestamp');
    expect(res.body).toHaveProperty('uptime');
  });
});

describe('Root Endpoint', () => {
  it('should return API information', async () => {
    const res = await request(app)
      .get('/')
      .expect(200);

    expect(res.body).toHaveProperty('name', 'OneRoster Gradebook Service');
    expect(res.body).toHaveProperty('version', '1.2.0');
    expect(res.body).toHaveProperty('endpoints');
  });
});
