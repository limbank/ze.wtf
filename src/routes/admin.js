const { Router } = require('express');
const router = Router();

//check for users and also check if user is an administrator
const isAuth = (req, res, next) => req.isAuthenticated() ? next() : res.errorRedir('error', 'You must be logged in to do that', '/auth/login');

module.exports = (connection) => {

    router.get('/', isAuth, (req, res) => res.redirect('/admin/links'));
    router.get('/links', isAuth, (req, res) => res.frender('admin/links'));
    router.get('/users', isAuth, (req, res) => res.frender('admin/users'));
    router.get('/stats', isAuth, (req, res) => res.frender('admin/stats'));

    return router;
};