const OAuth2Server = require('oauth2-server');
const { model } = require('../config/oauth');
const logger = require('../utils/logger');

const Request = OAuth2Server.Request;
const Response = OAuth2Server.Response;

/**
 * Initialize OAuth2 Server
 */
const oauth = new OAuth2Server({
  model,
  accessTokenLifetime: parseInt(process.env.OAUTH_TOKEN_LIFETIME || '3600', 10),
  allowBearerTokensInQueryString: false,
  allowEmptyState: false,
  authorizationCodeLifetime: 300,
  requireClientAuthentication: {
    client_credentials: true,
  },
});

/**
 * Token endpoint middleware
 * POST /oauth/token
 * Implements OAuth 2.0 Client Credentials Grant
 */
const token = async (req, res, next) => {
  const request = new Request(req);
  const response = new Response(res);

  try {
    logger.info('Token request received', {
      grantType: req.body.grant_type,
      clientId: req.body.client_id,
    });

    const token = await oauth.token(request, response);

    logger.info('Token issued successfully', {
      clientId: token.client.id,
      expiresAt: token.accessTokenExpiresAt,
      scope: token.scope,
    });

    res.json({
      access_token: token.accessToken,
      token_type: 'Bearer',
      expires_in: Math.floor((token.accessTokenExpiresAt - new Date()) / 1000),
      scope: token.scope,
    });
  } catch (error) {
    logger.error('Token request failed', {
      error: error.message,
      name: error.name,
    });

    // Return OAuth 2.0 error format
    res.status(error.code || 500).json({
      error: error.name || 'server_error',
      error_description: error.message || 'An error occurred',
    });
  }
};

/**
 * Authenticate middleware
 * Validates Bearer token and attaches user/client to request
 * @param {Object} options - Middleware options
 * @param {string|string[]} options.scope - Required scope(s)
 */
const authenticate = (options = {}) => {
  return async (req, res, next) => {
    const request = new Request(req);
    const response = new Response(res);

    try {
      const token = await oauth.authenticate(request, response, options);

      // Attach token info to request
      req.oauth = {
        token: token.accessToken,
        user: token.user,
        client: token.client,
        scope: token.scope,
      };

      logger.debug('Request authenticated', {
        clientId: token.client.id,
        scope: token.scope,
      });

      next();
    } catch (error) {
      logger.warn('Authentication failed', {
        error: error.message,
        path: req.path,
        method: req.method,
      });

      // Return OneRoster error format for authentication failures
      const statusCode = error.code || 401;
      const imsx_codeMajor = statusCode === 401 ? 'failure' : 'failure';
      const imsx_severity = 'error';
      const imsx_description = error.message || 'Authentication failed';
      const imsx_codeMinor = statusCode === 401 
        ? 'unauthorized' 
        : (statusCode === 403 ? 'forbidden' : 'server_error');

      res.status(statusCode).json({
        imsx_codeMajor,
        imsx_severity,
        imsx_description,
        imsx_codeMinor,
      });
    }
  };
};

/**
 * Require specific scope middleware
 * @param {string|string[]} scope - Required scope(s)
 */
const requireScope = (scope) => {
  return async (req, res, next) => {
    try {
      if (!req.oauth || !req.oauth.scope) {
        logger.warn('No OAuth scope found in request');
        return res.status(403).json({
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'Insufficient scope',
          imsx_codeMinor: 'forbidden',
        });
      }

      const tokenScopes = Array.isArray(req.oauth.scope) 
        ? req.oauth.scope 
        : req.oauth.scope.split(' ');
      
      const requiredScopes = Array.isArray(scope) 
        ? scope 
        : [scope];

      const hasScope = requiredScopes.some(s => tokenScopes.includes(s));

      if (!hasScope) {
        logger.warn('Insufficient scope', {
          required: requiredScopes,
          provided: tokenScopes,
        });

        return res.status(403).json({
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: `Required scope: ${requiredScopes.join(' or ')}`,
          imsx_codeMinor: 'forbidden',
        });
      }

      next();
    } catch (error) {
      logger.error('Error in requireScope middleware', error);
      next(error);
    }
  };
};

/**
 * OneRoster scopes
 */
const SCOPES = {
  // Read scopes
  ROSTER_READONLY: 'https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly',
  ROSTER_CORE_READONLY: 'https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly',
  
  // Write scopes
  LINEITEM_WRITE: 'https://purl.imsglobal.org/spec/or/v1p2/scope/lineitem',
  LINEITEM_READONLY: 'https://purl.imsglobal.org/spec/or/v1p2/scope/lineitem.readonly',
  
  RESULT_WRITE: 'https://purl.imsglobal.org/spec/or/v1p2/scope/result',
  RESULT_READONLY: 'https://purl.imsglobal.org/spec/or/v1p2/scope/result.readonly',
};

module.exports = {
  oauth,
  token,
  authenticate,
  requireScope,
  SCOPES,
};
