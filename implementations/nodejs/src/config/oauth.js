const crypto = require('crypto');
const logger = require('../utils/logger');

/**
 * OAuth 2.0 Client Credentials Grant Implementation
 * Implements IMS Global OneRoster Security Framework
 */

// In-memory storage (replace with database in production)
const tokens = new Map();
const clients = new Map();

/**
 * Load OAuth clients from environment variables
 * Format: OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET
 */
function loadClients() {
  const clientId = process.env.OAUTH_CLIENT_ID;
  const clientSecret = process.env.OAUTH_CLIENT_SECRET;
  const clientScopes = process.env.OAUTH_CLIENT_SCOPES 
    ? process.env.OAUTH_CLIENT_SCOPES.split(',').map(s => s.trim())
    : ['https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly'];

  if (clientId && clientSecret) {
    clients.set(clientId, {
      clientId,
      clientSecret,
      grants: ['client_credentials'],
      scopes: clientScopes,
    });
    logger.info(`OAuth client loaded: ${clientId}`);
  } else {
    logger.warn('No OAuth clients configured. Set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET.');
  }
}

// Load clients on initialization
loadClients();

/**
 * OAuth 2.0 Model for oauth2-server
 */
const model = {
  /**
   * Get client by client_id and client_secret
   * @param {string} clientId - Client ID
   * @param {string} clientSecret - Client Secret
   * @returns {Object|null} Client object or null
   */
  getClient: async (clientId, clientSecret) => {
    try {
      const client = clients.get(clientId);
      
      if (!client) {
        logger.warn(`Client not found: ${clientId}`);
        return null;
      }

      // Verify client secret
      if (client.clientSecret !== clientSecret) {
        logger.warn(`Invalid client secret for client: ${clientId}`);
        return null;
      }

      logger.info(`Client authenticated: ${clientId}`);
      return {
        id: client.clientId,
        clientId: client.clientId,
        grants: client.grants,
        redirectUris: [],
        scopes: client.scopes,
      };
    } catch (error) {
      logger.error('Error in getClient:', error);
      return null;
    }
  },

  /**
   * Get user (not used for Client Credentials Grant)
   * @returns {Object} Empty user object
   */
  getUserFromClient: async (client) => {
    try {
      // For Client Credentials Grant, there is no user
      // Return a service account object
      logger.info(`Creating service account for client: ${client.clientId}`);
      return {
        id: client.clientId,
        username: client.clientId,
      };
    } catch (error) {
      logger.error('Error in getUserFromClient:', error);
      return null;
    }
  },

  /**
   * Save access token
   * @param {Object} token - Token data
   * @param {Object} client - Client object
   * @param {Object} user - User object
   * @returns {Object} Saved token
   */
  saveToken: async (token, client, user) => {
    try {
      const accessToken = {
        accessToken: token.accessToken,
        accessTokenExpiresAt: token.accessTokenExpiresAt,
        scope: token.scope,
        client: {
          id: client.clientId,
          grants: client.grants,
        },
        user: {
          id: user.id,
          username: user.username,
        },
      };

      tokens.set(token.accessToken, accessToken);
      logger.info(`Token saved for client: ${client.clientId}, expires: ${token.accessTokenExpiresAt}`);
      
      return accessToken;
    } catch (error) {
      logger.error('Error in saveToken:', error);
      throw error;
    }
  },

  /**
   * Get access token
   * @param {string} accessToken - Access token string
   * @returns {Object|null} Token object or null
   */
  getAccessToken: async (accessToken) => {
    try {
      const token = tokens.get(accessToken);
      
      if (!token) {
        logger.warn('Token not found');
        return null;
      }

      // Check if token is expired
      if (token.accessTokenExpiresAt < new Date()) {
        logger.warn('Token expired');
        tokens.delete(accessToken);
        return null;
      }

      logger.debug(`Token found for client: ${token.client.id}`);
      return token;
    } catch (error) {
      logger.error('Error in getAccessToken:', error);
      return null;
    }
  },

  /**
   * Verify scope
   * @param {Object} token - Token object
   * @param {string|string[]} scope - Required scope(s)
   * @returns {boolean} True if scope is valid
   */
  verifyScope: async (token, scope) => {
    try {
      if (!token.scope) {
        logger.warn('Token has no scope');
        return false;
      }

      const tokenScopes = Array.isArray(token.scope) 
        ? token.scope 
        : token.scope.split(' ');
      
      const requiredScopes = Array.isArray(scope) 
        ? scope 
        : scope.split(' ');

      const hasScope = requiredScopes.every(s => tokenScopes.includes(s));
      
      if (!hasScope) {
        logger.warn(`Insufficient scope. Required: ${requiredScopes}, Token has: ${tokenScopes}`);
      }
      
      return hasScope;
    } catch (error) {
      logger.error('Error in verifyScope:', error);
      return false;
    }
  },

  /**
   * Generate access token
   * @returns {string} Access token
   */
  generateAccessToken: async (client, user, scope) => {
    try {
      // Generate a secure random token
      const token = crypto.randomBytes(32).toString('hex');
      logger.debug(`Generated token for client: ${client.clientId}`);
      return token;
    } catch (error) {
      logger.error('Error in generateAccessToken:', error);
      throw error;
    }
  },

  /**
   * Get access token expiration date
   * @returns {Date} Expiration date
   */
  getAccessTokenExpiresAt: () => {
    const expiresIn = parseInt(process.env.OAUTH_TOKEN_LIFETIME || '3600', 10);
    return new Date(Date.now() + expiresIn * 1000);
  },
};

/**
 * Add a new OAuth client (for testing/admin purposes)
 * @param {string} clientId - Client ID
 * @param {string} clientSecret - Client Secret
 * @param {string[]} scopes - Allowed scopes
 * @returns {Object} Created client
 */
function addClient(clientId, clientSecret, scopes = []) {
  const client = {
    clientId,
    clientSecret,
    grants: ['client_credentials'],
    scopes,
  };
  clients.set(clientId, client);
  logger.info(`OAuth client added: ${clientId}`);
  return client;
}

/**
 * Remove an OAuth client
 * @param {string} clientId - Client ID
 * @returns {boolean} True if removed
 */
function removeClient(clientId) {
  const removed = clients.delete(clientId);
  if (removed) {
    logger.info(`OAuth client removed: ${clientId}`);
  }
  return removed;
}

/**
 * Revoke a token
 * @param {string} accessToken - Access token to revoke
 * @returns {boolean} True if revoked
 */
function revokeToken(accessToken) {
  const revoked = tokens.delete(accessToken);
  if (revoked) {
    logger.info('Token revoked');
  }
  return revoked;
}

/**
 * Clean up expired tokens (should be run periodically)
 */
function cleanupExpiredTokens() {
  const now = new Date();
  let count = 0;
  
  for (const [token, data] of tokens.entries()) {
    if (data.accessTokenExpiresAt < now) {
      tokens.delete(token);
      count++;
    }
  }
  
  if (count > 0) {
    logger.info(`Cleaned up ${count} expired tokens`);
  }
}

// Run cleanup every hour
if (process.env.NODE_ENV !== 'test') {
  setInterval(cleanupExpiredTokens, 3600000);
}

module.exports = {
  model,
  addClient,
  removeClient,
  revokeToken,
  cleanupExpiredTokens,
};
