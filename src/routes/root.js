const { Router } = require('express');
const router = Router();
const { recaptcha } = require('../functions');
const { body, validationResult } = require('express-validator');
const axios = require('axios');
const moment = require('moment');

module.exports = () => {

    router.get('/', (req, res) => res.redirect('/home'));
    router.get('/home', (req, res) => res.frender('home'));
    router.get('/contact', (req, res) => res.frender('contact'));

    router.post('/contact', recaptcha.middleware, [
        body('email').isEmail().withMessage('You must give a valid email').custom((val, { req }) => {
            if (!val) throw new Error('You must give a value for email');
            return true;
        }),
        body('discord').custom((val, { req }) => {
            if (!val) return true;
            if (!val.match(/^([^]){1,32}#(\d){4}/gi)) throw new Error('Invalid Discord given');
            return true;
        }),
        body('name').custom((val, { req }) => {
            if (!val) throw new Error('You must give a value for name');
            if (val.length > 32) throw new Error('You can\'t give a name longer than 32 characters long');
            return true; 
        }),
        body('subject').custom((val, { req }) => {
            if (!val) throw new Error('You must give a value for subject');
            if (val.length > 64) throw new Error('You can\'t give a subject longer than 64 characters long');
            return true;
        }),
        body('message').custom((val, { req }) => {
            if (!val) throw new Error('You must give a value for message');
            if (val.length > 1000) throw new Error('You can\'t give a message longer than 1000 characters long');
            return true;
        })
    ], (req, res) => {
        const errors = validationResult(req).errors;
        if (errors.length > 0) {
            res.errorRedir('error', errors[0].msg, '/contact');
        } else {
            axios(`https://discord.com/api/webhooks/${process.env.CONTACT_WEBHOOK_ID}/${process.env.CONTACT_WEBHOOK_TOKEN}`, {
                method: 'POST',
                data: {
                    embeds: [
                        {
                            title: 'New Message',
                            color: 3570146,
                            description: `**Time**: ${moment().format('MMMM Do YYYY, h:mm a')}\n**Logged in**? ${!!req.user}\n${req.user ? `**Username**: ${req.user.username}\n**User ID**: ${req.user.user_id}` : ''}`,
                            fields: Object.entries(req.body).map(x => ({
                                name: x[0][0].toUpperCase() + x[0].slice(1),
                                value: x[1],
                                inline: false
                            })).filter(x => (x.name.trim() != '' && x.value.trim() != '')),
                            footer: {
                                text: 'ZE.WTF - Contact',
                                icon_url: 'https://cdn.discordapp.com/attachments/738049160606908466/751947025485922304/templogo.png'
                            },
                        }
                    ]
                }
            })
            .then(axi => {
                res.errorRedir('success', 'Message sent!', '/contact');
            })
            .catch(e => {
                console.log(e)
                res.errorRedir('error', 'Error in sending your message', '/contact');
            });
        };
    });

    return router;
};