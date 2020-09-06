const { Router } = require('express');
const router = Router();

module.exports = () => {

    router.get('/', (req, res) => res.redirect('/home'));

    router.get('/home', (req, res) => res.render('home', { theme: req.theme }));

    router.get('/contact', (req, res) => res.render('contact', { theme: req.theme }));
    
    return router;
};