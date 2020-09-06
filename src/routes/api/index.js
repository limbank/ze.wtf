module.exports = (server, ...imports) => {
    server.use('/api/themes', require('./theme.js')(...imports));
};