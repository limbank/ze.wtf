const path = require('path');
const express = require('express');
const mysql = require('mysql');
const rateLimit = require('express-rate-limit');
const logSymbols = require('log-symbols');
const chalk = require('chalk');
const morgan = require('morgan');
const session = require('express-session');
const MySQLStore = require('express-mysql-session')(session);
const cookieParser = require('cookie-parser');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const { compareSync } = require('bcrypt');

require('dotenv').config({ path: path.join(__dirname, './config/.env') });
const server = express();

const connection = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME
});

const sessionStore = new MySQLStore({
    clearExpired: true,
    checkExpirationInterval: 900000,
    createDatabaseTable: true,
    charset: 'utf8mb4_bin',
    endConnectionOnClose: true,
    schema: {
        tableName: 'sessions',
        columnNames: {
            session_id: 'session_id',
            expires: 'expires',
            data: 'data'
        }
    }
}, connection);

passport.serializeUser((user, done) => done(null, user.user_id));

passport.deserializeUser(function(id, done) {
    connection.query("SELECT * FROM users WHERE user_id = ?", id, (error, rows) => {
        done(error, rows[0]);
    });
});

passport.use(
    'local-login',
    new LocalStrategy({
        usernameField : 'username',
        passwordField : 'password',
        passReqToCallback : true
    },
    function(req, username, password, done) {
        connection.query("SELECT * FROM users WHERE username = ? OR email = ?", [username, username], (error, rows) => {
            if (error) return done(error);
            if (!rows.length) return done(null, false);
            if (!compareSync(password, rows[0].password)) return done(null, false);
            return done(null, rows[0]);
        });  
    })
);

connection.connect(error => {
    if (error) return (console.log(`${logSymbols.error} [${chalk.bold.magenta('MYSQL')}] Error in connecting to the database.`));
    console.log(`${logSymbols.success} [${chalk.bold.magenta('MYSQL')}] Connected to the database "${process.env.DB_NAME}" with the host "${process.env.DB_HOST}"`)
});

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 150,
    handler: (req, res) => res.status(429).json({ error: 'Too Many Requests' })
});

server.use('/resources', express.static(path.join(__dirname, './resources')));

server.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: true,
}));

server.use(passport.initialize());
server.use(passport.session());
server.set('view engine', 'ejs');
server.set('views', path.join(__dirname, './views'));
server.use(cookieParser());
server.use(morgan('dev'));
server.use(limiter);
server.use((req, res, next) => {
    req.theme = req.cookies.theme ? ['dark', 'light'].includes(req.cookies.theme) ? req.cookies.theme : 'light' : 'light';
    res.error = (opt = {}) => {
        if (typeof opt == 'string') opt = { title: opt };
        res.render('handlers/error', {
            title: opt.title ? opt.title : '500',
            subtitle: opt.subtitle ? opt.subtitle : undefined
        });
    };
    res.frender = (file, opt = {}) => {
        return res.render(file, { ...opt, theme: req.theme, user: req.user, error: req.query.error });
    };
    res.errorRedir = (type, message, link) => {
        return res.redirect(`${link}?${type}=${message}`);
    };
    next();
});

server.use('/', require('./routes/root.js')());
server.use('/auth', require('./routes/auth.js')(connection));
server.use('/user', require('./routes/user.js')(connection));
require('./routes/api')(server);

server.use((req, res, next) => res.error('404'));
server.use((error, req, res, next) => {
    console.log(error);
    if (res.error) {
        res.error('500');
    } else {
        res.status(500).json({ error: '500 - Internal Error' });
    };
});

server.listen(process.env.PORT, () => console.log(`${logSymbols.success} [${chalk.bold.blue('EXPRESS')}] Ze.WTF started on port ${process.env.PORT}!`));