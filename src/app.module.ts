import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { APP_FILTER, APP_GUARD, APP_INTERCEPTOR } from "@nestjs/core";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { WinstonModule } from "nest-winston";
import { typeormConfig } from "@config/typeorm.config";
import { winstonConfig } from "@config/logger.config";
import { validate } from "@config/env.validation";
import { DatabaseModule } from "@database/database.module";
import { HttpExceptionFilter } from "@common/filters/http-exception.filter";
import { TransformInterceptor } from "@common/interceptors/transform.interceptor";
import { JwtAuthGuard } from "@common/guards/jwt-auth.guard";
import { RolesGuard } from "@common/guards/roles.guard";
import { HealthModule } from "@common/health/health.module";
import { AuthModule } from "@modules/auth/auth.module";
import { UsersModule } from "@modules/users/users.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
      load: [typeormConfig],
      envFilePath: [".env.local", ".env"],
    }),
    // Winston logger — replaces NestJS built-in logger globally
    WinstonModule.forRoot(winstonConfig),
    // FIX: rate limiting — short burst + per-minute window
    ThrottlerModule.forRoot([
      { name: "short", ttl: 1000, limit: 10 },
      { name: "medium", ttl: 60000, limit: 100 },
    ]),
    DatabaseModule,
    HealthModule,
    AuthModule,
    UsersModule,
  ],
  providers: [
    { provide: APP_FILTER, useClass: HttpExceptionFilter },
    { provide: APP_INTERCEPTOR, useClass: TransformInterceptor },
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: RolesGuard },
    // FIX: global throttler guard
    { provide: APP_GUARD, useClass: ThrottlerGuard },
  ],
})
export class AppModule {}
