module.exports = (server, ...imports) => {
    server.use('/api/themes', require('./theme.js')(...imports));
    server.use('/api/links', require('./theme.js')(...imports));
};