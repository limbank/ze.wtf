const { Router } = require('express');
const router = Router();

module.exports = (a, b) => {

    router.get('/set/:theme', async (req, res) => {
        if (!['dark', 'light'].includes(req.params.theme)) return res.json({ error: 'Theme not found.' });
        res.cookie('theme', req.params.theme);
        res.json({ message: 'Theme set!' });
    });
    
    return router;
};