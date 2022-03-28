'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  SERVER_BASE_URL: '"http://127.0.0.1:15555"',
  SERVER_DOMAIN: '"127.0.0.1"'
})
