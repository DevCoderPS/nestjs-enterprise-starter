import { registerAs } from '@nestjs/config';
import { DataSource, DataSourceOptions } from 'typeorm';

export const typeormConfig = registerAs('typeorm', (): DataSourceOptions => ({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  migrations: [__dirname + '/../database/migrations/*{.ts,.js}'],
  // FIX: synchronize only when explicitly allowed in development — never staging/production
  synchronize:
    process.env.NODE_ENV === 'development' &&
    process.env.ALLOW_SYNC === 'true',
  logging: process.env.NODE_ENV === 'development',
  extra: {
    max: 20,
    min: 2,
    connectionTimeoutMillis: 5000,
    idleTimeoutMillis: 30000,
    // FIX: kill slow/hung queries
    statement_timeout: 10000,
    query_timeout: 10000,
    // Identify this app in pg_stat_activity
    application_name: 'projectx-api',
  },
  ssl:
    process.env.NODE_ENV === 'production'
      ? { rejectUnauthorized: false }
      : false,
}));

export const AppDataSource = new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  migrations: [__dirname + '/../database/migrations/*{.ts,.js}'],
  synchronize: false,
  extra: { max: 20, application_name: 'projectx-cli' },
});
