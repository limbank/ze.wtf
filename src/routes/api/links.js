const { Router } = require('express');
const router = Router();
const crs = require('crypto-random-string');
const moment = require('moment');

module.exports = (connection) => {

    // Create read update delete

    const auth = (req, res, next) => {
        if (req.body.key) {
            connection.query('SELECT owner_id, permissions FROM api_keys WHERE api_key = ?', req.body.key, (error, data) => {
                if (error) return res.status(500).json({ error: 'Internal database error. Please try again' });
                if (!data[0]) return res.status(401).json({ error: 'Invalid API key or user id.' });
                const permissions = data[0].permissions.split('');
                req.auth = {
                    user_id: data[0].owner_id,
                    isAuthorised: true,
                    permissions: {
                        create: permissions.includes('c'),
                        read: permissions.includes('r'),
                        update: permissions.includes('u'),
                        delete: permissions.includes('d')
                    }
                }
                next();
            });
        } else if (req.isAuthenticated()) {
            req.auth = {
                user_id: req.user.user_id,
                isAuthorised: true,
                permissions: {
                    create: true,
                    read: true,
                    update: true,
                    delete: true
                }
            };
            next();
        } else {
            req.auth = {
                user_id: undefined,
                isAuthorised: false,
                permissions: {
                    create: true,
                    read: true,
                    update: false,
                    delete: false
                }
            };
            next();
        };
    };

    const asyncSQL = (query, escapes) => new Promise((resolve, reject) => {
        connection.query(query, escapes, (error, data) => {
            if (error) return resolve({ error });
            resolve({ data });
        });
    });

    function generateID() {
        return new Promise(async (resolve, reject) => {
            let foundID = false;
            let times = 0;

            while(!foundID) {
                if (times > 10) return (foundID = true, reject('Generating error'));
                const id = crs({ length: Number(process.env.RANDOM_LINK_LENGTH), type: 'url-safe' });
                const data = await asyncSQL('SELECT id FROM links WHERE id = ?', id);
                if (data.error) return (foundID = true, reject('Database error'));
                if (!data.data[0]) return (foundID = true, resolve(id));
                times++;
            };
        });
    };

    router.post('/create', auth, async (req, res) => {
        if (req.auth.permissions.create) {
            const from = req.body.link;
            const time = Date.now();
            const id = await generateID();
            console.log(req.body)
            const redirectsTo = req.body.redirectURL;
            if (!redirectsTo) return res.status(400).json({ error: 'RedirectURL missing' });
            if (!redirectsTo.match(/[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/ig)) return res.status(400).json({ error: 'Invalid redirectURL' });
            connection.query('INSERT INTO links (id, owner_id, redirects_to, created_timestamp) VALUES (?, ?, ?, ?)', [id, req.auth.isAuthorised ? req.auth.user_id : null, redirectsTo, time], error => {
                if (error) return res.status(500).json({ error: 'Internal Error. Please try again' });
                res.status(201).json({ message: 'Link created', link: `https://ze.wtf/${id}`, timestamp_created: time, isAuthorised: req.auth.isAuthorised });
            });
        } else {
            return res.status(401).json({ error: 'Not Authorised' });
        };
    });

    return router;
};