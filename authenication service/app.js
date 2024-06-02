const express = require('express');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/authentication');

const app = express();
app.use(bodyParser.json());

app.use('/auth', authRoutes);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Authentication service running on port ${PORT}`);
});