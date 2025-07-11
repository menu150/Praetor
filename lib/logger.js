import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  transports: [
    new winston.transports.File({ filename: 'logs/errors.log' }),
    new winston.transports.Console(),
  ],
});

export default logger;
