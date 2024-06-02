const { Pool } = require('pg');
const { db } = require('../utilities/config');

const pool = new Pool(db);

module.exports = pool;