import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DataSourceOptions } from 'typeorm';

@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService): DataSourceOptions => {
        const options = configService.get<DataSourceOptions>('typeorm');
        if (!options) {
          throw new Error('TypeORM configuration not found');
        }
        return options;
      },
    }),
  ],
})
export class DatabaseModule {}
