require('dotenv').config();

module.exports = {
    jwtSecretKey: process.env.JWT_SECRET_KEY,
    db: {
        user: process.env.DB_USER,
        host: process.env.DB_HOST,
        database: process.env.DB_NAME,
        password: process.env.DB_PASSWORD,
        port: process.env.DB_PORT,
    },
};