const { Router } = require('express');
const router = Router();

module.exports = () => {

    router.get('/', (req, res) => res.redirect('/docs/intro'));
    router.get('/intro', (req, res) => res.frender('docs/intro'));
    router.get('/create', (req, res) => res.frender('docs/create'));
    router.get('/read', (req, res) => res.frender('docs/read'));
    router.get('/update', (req, res) => res.frender('docs/update'));
    router.get('/delete', (req, res) => res.frender('docs/delete'));

    return router;
};