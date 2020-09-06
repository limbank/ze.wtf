const { Router } = require('express');
const router = Router();

const isAuth = (req, res, next) => req.isAuthenticated() ? next() : res.errorRedir('error', 'You must be logged in to do that', '/auth/login');

module.exports = (connection) => {

    router.get('/', isAuth, (req, res) => res.redirect('/user/links'));
    router.get('/links', isAuth, (req, res) => res.frender('user/links'));

    return router;
};