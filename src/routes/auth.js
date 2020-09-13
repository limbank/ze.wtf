const { Router } = require('express');
const router = Router();
const { authenticate } = require('passport');
const { body, validationResult } = require('express-validator');
const { urlencoded } = require('body-parser');
const FlakeId = require('flakeid');
const { hash } = require('bcrypt');

const flake = new FlakeId({ timeOffset : (2013-1970)*31536000*1000 });  

module.exports = (connection) => {

    const asyncSQL = (query, escapes) => new Promise((resolve, reject) => {
        connection.query(query, escapes, (error, data) => {
            if (error) return resolve({ error });
            resolve({ data });
        });
    });

    router.get('/login', (req, res, next) => req.isAuthenticated() ? res.redirect('/user') : next(), (req, res) => res.frender('login'));
    router.get('/signup', (req, res, next) => req.isAuthenticated() ? res.redirect('/user') : next(), (req, res) => res.frender('signup'));

    router.get('/logout', (req, res) => {
        req.logOut();
        res.redirect('/');
    });

    router.post('/login', passport.authenticate('local-login', {
        successRedirect: '/user',
        failureRedirect: '/auth/login?error=Error in logging in'
    }));

    router.post('/signup', [
        body('email').isEmail().withMessage('You must give a valid email').custom(async (val, { req }) => {
            const x = await asyncSQL('SELECT email FROM users WHERE email = ?', val);
            if (x.error) throw new Error('Database error. Please try again');
            if (x.data[0]) throw new Error('Email has already been taken');
            return true;
        }),
        body('username').custom(async (val, { req }) => {
            if (val.length < 4) throw new Error('Username can\'t be shorter than 4 characters');
            if (val.length > 32) throw new Error('Username can\'t be longer than 32 characters');
            const x = await asyncSQL('SELECT username FROM users WHERE username = ?', val);
            if (x.error) throw new Error('Database error. Please try again');
            if (x.data[0]) throw new Error('Username has already been taken');
            return true;
        }),
        body('password').custom((val, { req }) => {
            if (!val.match(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/gm)) throw new Error('Password must be at least 6 characters long, with one uppercase and lowercase letter, and a number.');
            if (val != req.body.passwordconfirm) throw new Error('Passwords do not match');
            return true;
        }),
    ], (req, res) => {
        const errors = validationResult(req).errors;
        if (errors.length > 0) {
            res.errorRedir('error', errors[0].msg, '/auth/signup');
        } else {
            hash(req.body.password, 10, function(error, hash) {
                if (error) return res.errorRedir('error', 'Error in signing up. Please try again', '/auth/signup');
                connection.query('INSERT INTO users (username, user_id, password, email, joined_timestamp) VALUES (?, ?, ?, ?, ?)', [req.body.username, flake.gen(), hash, req.body.email, Date.now()], error => {
                    if (error) return res.errorRedir('error', 'Error in signing up. Please try again', '/auth/signup');
                    res.redirect('/auth/login');
                });
            });
        };
    });
    
    return router;
};