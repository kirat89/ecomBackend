const {Router} = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { registerUser, findUserByUsername,findrolesByUserID ,findroleByname,registerUserRole} = require('../database/queries');
const { jwtSecretKey } = require('../utilities/config');


const router = Router();



// Register endpoint
router.post('/register', async (req, res) => {
    const { email,username, password, rolename  } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = await registerUser(username,email, hashedPassword);
        const role_id = await findroleByname(rolename.toLowerCase())
        await registerUserRole(user.id,role_id.id)
        res.status(201).json(user);
    } catch (error) {
        console.error('Error during user registration:', error);
        res.status(500).send('Server error');
    }
});

// Login endpoint
router.post('/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        const user = await findUserByUsername(username);
        if (user && await bcrypt.compare(password, user.password)) {
            const roles = await findrolesByUserID(user.id);
            let role_list  = []
            roles.map((obj)=>{
                role_list.push(obj.role_name)
            })
            const token = jwt.sign({ id: user.id, username: user.username, roles: roles}, jwtSecretKey, { expiresIn: '1h' });
            res.json({ token });
        } else {
            res.status(401).send('Invalid credentials');
        }
    } catch (error) {
        console.error('Error during user login:', error);
        res.status(500).send('Server error');
    }
});


router.post('/validateToken', async (req, res) => {
    const token = req.body.token;
 
    if (token) {
        const decode = jwt.verify(token, jwtSecretKey);
        res.json({
            login: true,
            data: decode,
        });
    } else {

        res.json({
            login: false,
            data: "error",
        });
    }
});


module.exports = router;
