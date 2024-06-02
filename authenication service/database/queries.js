const pool = require('./index');

// Register a new user
const registerUser = async (username,email, hashedPassword) => {
    const result = await pool.query(
        'INSERT INTO users (username,email, password) VALUES ($1, $2, $3) RETURNING *',
        [username,email, hashedPassword]
    );
    console.log(result);
    return result.rows[0];
};

const registerUserRole = async (userID,roleID ) => {
    const result = await pool.query(
        'INSERT INTO user_role_map (user_id, role_id) VALUES ($1, $2) RETURNING *',
        [userID,roleID]
    );
    
    return result.rows[0];
};
const findroleByname = async (rolename) => {
    const result = await pool.query(
        'SELECT * FROM roles WHERE lower(role_name) = $1',
        [rolename]
    );
    return result.rows[0];
};

const findrolesByUserID = async (userId) => {
    const result = await pool.query(
        'SELECT distinct(role_name) role_name FROM roles r join user_role_map urm on r.id = urm.role_id and urm.user_id = $1',
        [userId]
    );
    return result.rows;
};

// Find a user by username
const findUserByUsername = async (username) => {
    const result = await pool.query(
        'SELECT * FROM users WHERE username = $1',
        [username]
    );
    return result.rows[0];
};


// const findUserandRolesByUsername = async (username) => {
//     const result = await pool.query(
//         'SELECT u.username,u.password ,ur.user_id,ur.role_id FROM user_role_map ur join users u on u.user_id = ur.user_id and  username = $1',
//         [username]
//     );
//     return result.rows;
// };

module.exports = {
    registerUser,
    findrolesByUserID,
    findUserByUsername,
    findroleByname,
    registerUserRole
};
