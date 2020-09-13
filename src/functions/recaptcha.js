const { URLSearchParams } = require('url');
const axios = require('axios');

async function middleware(req, res, next) {
    try {
        const { success } = await check(req.body['g-recaptcha-response']);
        if (success) {
            next();
        } else {
            res.redirect(`${req.originalUrl}?error=Please complete the reCaptcha`);
        };
    }
    catch(error) {
        console.log(error)
        res.redirect(`${req.originalUrl}?error=Error in checking the reCaptcha`);
    }
};

function check(response = '') {
    return new Promise((resolve, reject) => {
        axios.post('https://www.google.com/recaptcha/api/siteverify', new URLSearchParams({
            secret: process.env.RECAPTCHA_SECRET,
            response: response
        }))
        .then(axi => resolve(axi.data))
        .catch(reject);
    });
};

module.exports = {
    middleware,
    check
};