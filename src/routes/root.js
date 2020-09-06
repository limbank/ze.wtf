const { Router } = require('express');
const router = Router();

module.exports = () => {

    router.get('/', (req, res) => res.redirect('/home'));
    router.get('/home', (req, res) => res.frender('home'));
    router.get('/contact', (req, res) => res.frender('contact'));
    
    return router;
};