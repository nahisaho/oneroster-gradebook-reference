const request = require('supertest');
const app = require('../../src/app');
const db = require('../../src/models');

describe('OAuth 2.0 Authentication', () => {
  beforeAll(async () => {
    // Ensure database connection
    await db.sequelize.authenticate();
  });

  afterAll(async () => {
    await db.sequelize.close();
  });

  describe('POST /oauth/token', () => {
    it('should issue token with valid client credentials', async () => {
      const res = await request(app)
        .post('/oauth/token')
        .type('form')
        .send({
          grant_type: 'client_credentials',
          client_id: process.env.OAUTH_CLIENT_ID || 'test_client',
          client_secret: process.env.OAUTH_CLIENT_SECRET || 'test_secret',
          scope: 'https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly',
        })
        .expect('Content-Type', /json/)
        .expect(200);

      expect(res.body).toHaveProperty('access_token');
      expect(res.body).toHaveProperty('token_type', 'Bearer');
      expect(res.body).toHaveProperty('expires_in');
      expect(res.body).toHaveProperty('scope');
    });

    it('should reject invalid client credentials', async () => {
      const res = await request(app)
        .post('/oauth/token')
        .type('form')
        .send({
          grant_type: 'client_credentials',
          client_id: 'invalid_client',
          client_secret: 'invalid_secret',
          scope: 'https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly',
        })
        .expect('Content-Type', /json/)
        .expect(400);

      expect(res.body).toHaveProperty('error');
    });

    it('should reject missing grant_type', async () => {
      const res = await request(app)
        .post('/oauth/token')
        .type('form')
        .send({
          client_id: process.env.OAUTH_CLIENT_ID || 'test_client',
          client_secret: process.env.OAUTH_CLIENT_SECRET || 'test_secret',
        })
        .expect('Content-Type', /json/)
        .expect(400);

      expect(res.body).toHaveProperty('error');
    });
  });

  describe('Authentication Middleware', () => {
    it('should reject requests without token', async () => {
      const res = await request(app)
        .get('/ims/oneroster/v1p2/categories')
        .expect('Content-Type', /json/)
        .expect(401);

      expect(res.body).toHaveProperty('imsx_codeMajor', 'failure');
      expect(res.body).toHaveProperty('imsx_codeMinor', 'unauthorized');
    });

    it('should reject requests with invalid token', async () => {
      const res = await request(app)
        .get('/ims/oneroster/v1p2/categories')
        .set('Authorization', 'Bearer invalid_token')
        .expect('Content-Type', /json/)
        .expect(401);

      expect(res.body).toHaveProperty('imsx_codeMajor', 'failure');
    });
  });
});
