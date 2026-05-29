import { utilities as nestWinstonModuleUtilities, WinstonModuleOptions } from 'nest-winston';
import * as winston from 'winston';

const { combine, timestamp, errors, json } = winston.format;

const devFormat = combine(
  timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  errors({ stack: true }),
  nestWinstonModuleUtilities.format.nestLike('ProjectX', {
    prettyPrint: true,
    colors: true,
  }),
);

const prodFormat = combine(
  timestamp(),
  errors({ stack: true }),
  json(), // structured — works with Datadog / CloudWatch / ELK
);

const isProd = process.env.NODE_ENV === 'production';

export const winstonConfig: WinstonModuleOptions = {
  level: process.env.LOG_LEVEL ?? (isProd ? 'warn' : 'debug'),
  format: isProd ? prodFormat : devFormat,
  transports: [
    new winston.transports.Console(),
    ...(isProd
      ? [
          new winston.transports.File({
            filename: 'logs/error.log',
            level: 'error',
            maxsize: 10 * 1024 * 1024, // 10 MB
            maxFiles: 5,
          }),
          new winston.transports.File({
            filename: 'logs/combined.log',
            maxsize: 10 * 1024 * 1024,
            maxFiles: 10,
          }),
        ]
      : []),
  ],
  exitOnError: false,
};
