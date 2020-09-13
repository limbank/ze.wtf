module.exports = (server, connection) => {
    server.use('/api/themes', require('./theme.js')());
    server.use('/api/links', require('./links.js')(connection));
};