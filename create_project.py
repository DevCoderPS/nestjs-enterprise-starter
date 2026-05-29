#!/usr/bin/env python3
import os, zipfile

FILES = {}

FILES["tsconfig.json"] = r"""{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "strictBindCallApply": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@config/*": ["src/config/*"],
      "@database/*": ["src/database/*"],
      "@common/*": ["src/common/*"],
      "@modules/*": ["src/modules/*"]
    }
  }
}"""

FILES["nest-cli.json"] = r"""{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true,
    "webpack": false,
    "tsConfigPath": "tsconfig.json",
    "plugins": ["@nestjs/swagger"],
    "assets": [],
    "watchAssets": false
  }
}"""

FILES[".env.example"] = r"""PORT=3000
DATABASE_URL=postgresql://postgres:password@localhost:5432/projectx
JWT_SECRET=change_me_to_a_very_long_random_secret_at_least_64_chars
JWT_REFRESH_SECRET=change_me_to_another_very_long_random_secret_64_chars
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
LOG_LEVEL=debug
ALLOW_SYNC=false"""

FILES["package.json"] = r"""{
  "name": "projectx-backend",
  "version": "1.0.0",
  "description": "Enterprise NestJS Starter Boilerplate",
  "author": "",
  "private": true,
  "license": "UNLICENSED",
  "scripts": {
    "build": "nest build",
    "format": "prettier --write \"src/**/*.ts\"",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "typeorm": "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/config": "^3.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/jwt": "^10.0.0",
    "@nestjs/passport": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/swagger": "^7.0.0",
    "@nestjs/terminus": "^10.0.0",
    "@nestjs/throttler": "^5.0.0",
    "@nestjs/typeorm": "^10.0.0",
    "bcrypt": "^5.1.1",
    "class-transformer": "^0.5.1",
    "class-validator": "^0.14.0",
    "nest-winston": "^1.9.4",
    "passport": "^0.6.0",
    "passport-jwt": "^4.0.1",
    "pg": "^8.11.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1",
    "typeorm": "^0.3.17",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/bcrypt": "^5.0.2",
    "@types/express": "^4.17.17",
    "@types/jest": "^29.5.2",
    "@types/node": "^20.3.1",
    "@types/passport-jwt": "^3.0.9",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.42.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-prettier": "^5.0.0",
    "jest": "^29.5.0",
    "prettier": "^3.0.0",
    "source-map-support": "^0.5.21",
    "ts-jest": "^29.1.0",
    "ts-loader": "^9.4.3",
    "ts-node": "^10.9.1",
    "tsconfig-paths": "^4.2.0",
    "typescript": "^5.1.3"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": { "^.+\\.(t|j)s$": "ts-jest" },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node",
    "moduleNameMapper": {
      "^@config/(.*)$": "<rootDir>/config/$1",
      "^@database/(.*)$": "<rootDir>/database/$1",
      "^@common/(.*)$": "<rootDir>/common/$1",
      "^@modules/(.*)$": "<rootDir>/modules/$1"
    }
  }
}"""

# ─── Config ───────────────────────────────────────────────────────────────────

FILES["src/config/env.validation.ts"] = r"""import { plainToInstance } from 'class-transformer';
import {
  IsBoolean,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsString,
  Max,
  Min,
  validateSync,
} from 'class-validator';

class EnvironmentVariables {
  @IsInt()
  @Min(1)
  @Max(65535)
  PORT!: number;

  @IsString()
  @IsNotEmpty()
  DATABASE_URL!: string;

  @IsString()
  @IsNotEmpty()
  JWT_SECRET!: string;

  @IsString()
  @IsNotEmpty()
  JWT_REFRESH_SECRET!: string;

  @IsString()
  @IsOptional()
  LOG_LEVEL?: string;

  @IsBoolean()
  @IsOptional()
  ALLOW_SYNC?: boolean;
}

export function validate(config: Record<string, unknown>): EnvironmentVariables {
  const validatedConfig = plainToInstance(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });

  const errors = validateSync(validatedConfig, {
    skipMissingProperties: false,
  });

  if (errors.length > 0) {
    throw new Error(
      `Environment validation failed:\n${errors
        .map((e) => Object.values(e.constraints ?? {}).join(', '))
        .join('\n')}`,
    );
  }

  return validatedConfig;
}"""

FILES["src/config/typeorm.config.ts"] = r"""import { registerAs } from '@nestjs/config';
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
});"""

FILES["src/config/logger.config.ts"] = r"""import { utilities as nestWinstonModuleUtilities, WinstonModuleOptions } from 'nest-winston';
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
};"""

# ─── Database ─────────────────────────────────────────────────────────────────

FILES["src/database/database.module.ts"] = r"""import { Module } from '@nestjs/common';
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
export class DatabaseModule {}"""

# ─── Common — Base Entity ──────────────────────────────────────────────────────

FILES["src/common/base/audit.base.entity.ts"] = r"""import { Exclude, Expose } from 'class-transformer';
import {
  Column,
  CreateDateColumn,
  DeleteDateColumn,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';

export abstract class AuditBaseEntity {
  @Expose()
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Expose()
  @CreateDateColumn({ name: 'created_date', type: 'timestamptz' })
  createdDate!: Date;

  @Column({ name: 'created_by', type: 'varchar', length: 255, nullable: true })
  createdBy!: string | null;

  @Expose()
  @UpdateDateColumn({ name: 'updated_date', type: 'timestamptz' })
  updatedDate!: Date;

  @Column({ name: 'updated_by', type: 'varchar', length: 255, nullable: true })
  updatedBy!: string | null;

  @Exclude()
  @DeleteDateColumn({ name: 'deleted_date', type: 'timestamptz', nullable: true })
  deletedDate!: Date | null;
}"""

# ─── Common — Enums ───────────────────────────────────────────────────────────

FILES["src/common/enums/user-role.enum.ts"] = r"""export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  ADMIN = 'ADMIN',
  TEACHER = 'TEACHER',
  STUDENT = 'STUDENT',
  PARENT = 'PARENT',
}"""

# ─── Common — Decorators ──────────────────────────────────────────────────────

FILES["src/common/decorators/get-user.decorator.ts"] = r"""import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { Request } from 'express';
import { User } from '@modules/users/entities/user.entity';

export interface AuthenticatedRequest extends Request {
  user: User;
}

export const GetUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): User => {
    const request = ctx.switchToHttp().getRequest<AuthenticatedRequest>();
    return request.user;
  },
);"""

FILES["src/common/decorators/roles.decorator.ts"] = r"""import { SetMetadata } from '@nestjs/common';
import { UserRole } from '@common/enums/user-role.enum';

export const ROLES_KEY = 'roles';

export const Roles = (...roles: UserRole[]) => SetMetadata(ROLES_KEY, roles);"""

# FIX: single source of truth for Public decorator — removed duplication
FILES["src/common/decorators/public.decorator.ts"] = r"""import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';

/**
 * Mark a route as public — bypasses JwtAuthGuard globally.
 * Import from here; do NOT redefine elsewhere.
 */
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);"""

# ─── Common — Guards ──────────────────────────────────────────────────────────

FILES["src/common/guards/jwt-auth.guard.ts"] = r"""import {
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuthGuard } from '@nestjs/passport';
import { Observable } from 'rxjs';
import { IS_PUBLIC_KEY } from '@common/decorators/public.decorator';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private readonly reflector: Reflector) {
    super();
  }

  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (isPublic) {
      return true;
    }

    return super.canActivate(context);
  }

  handleRequest<TUser = unknown>(
    err: Error | null,
    user: TUser | false,
  ): TUser {
    if (err || !user) {
      throw err ?? new UnauthorizedException('Invalid or expired access token');
    }
    return user;
  }
}"""

FILES["src/common/guards/roles.guard.ts"] = r"""import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { UserRole } from '@common/enums/user-role.enum';
import { ROLES_KEY } from '@common/decorators/roles.decorator';
import { AuthenticatedRequest } from '@common/decorators/get-user.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>(
      ROLES_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const { user } = request;

    if (!user) {
      throw new ForbiddenException('Access denied: no authenticated user');
    }

    const hasRole = requiredRoles.some((role) => user.role === role);

    if (!hasRole) {
      throw new ForbiddenException(
        `Access denied: requires one of [${requiredRoles.join(', ')}]`,
      );
    }

    return true;
  }
}"""

# ─── Common — Filters ─────────────────────────────────────────────────────────

FILES["src/common/filters/http-exception.filter.ts"] = r"""import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

interface ErrorResponse {
  success: false;
  statusCode: number;
  path: string;
  message: string[];
  timestamp: string;
}

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let statusCode = HttpStatus.INTERNAL_SERVER_ERROR;
    let messages: string[] = ['Internal server error'];

    if (exception instanceof HttpException) {
      statusCode = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'string') {
        messages = [exceptionResponse];
      } else if (
        typeof exceptionResponse === 'object' &&
        exceptionResponse !== null
      ) {
        const body = exceptionResponse as Record<string, unknown>;
        if (Array.isArray(body['message'])) {
          messages = body['message'] as string[];
        } else if (typeof body['message'] === 'string') {
          messages = [body['message']];
        } else if (typeof body['error'] === 'string') {
          messages = [body['error']];
        }
      }
    } else if (exception instanceof Error) {
      messages = ['Internal server error'];
      this.logger.error(
        `Unhandled exception on ${request.method} ${request.url}: ${exception.message}`,
        exception.stack,
      );
    }

    const errorResponse: ErrorResponse = {
      success: false,
      statusCode,
      path: request.url,
      message: messages,
      timestamp: new Date().toISOString(),
    };

    response.status(statusCode).json(errorResponse);
  }
}"""

# ─── Common — Interceptors ────────────────────────────────────────────────────

FILES["src/common/interceptors/transform.interceptor.ts"] = r"""import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from '@nestjs/common';
import { map, Observable } from 'rxjs';

export interface TransformedResponse<T> {
  success: true;
  data: T;
  timestamp: string;
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, TransformedResponse<T>>
{
  intercept(
    _context: ExecutionContext,
    next: CallHandler<T>,
  ): Observable<TransformedResponse<T>> {
    return next.handle().pipe(
      map((data) => ({
        success: true,
        data,
        timestamp: new Date().toISOString(),
      })),
    );
  }
}"""

# ─── Common — Health ──────────────────────────────────────────────────────────

FILES["src/common/health/health.controller.ts"] = r"""import { Controller, Get, Logger } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckResult,
  HealthCheckService,
  MemoryHealthIndicator,
  TypeOrmHealthIndicator,
} from '@nestjs/terminus';
import { Public } from '@common/decorators/public.decorator';
import { ApiTags } from '@nestjs/swagger';

@ApiTags('Health')
@Controller('health')
export class HealthController {
  private readonly logger = new Logger(HealthController.name);

  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly memory: MemoryHealthIndicator,
  ) {}

  @Public()
  @Get()
  @HealthCheck()
  async check(): Promise<HealthCheckResult> {
    this.logger.debug('GET /health — running health checks');
    const result = await this.health.check([
      () => this.db.pingCheck('database'),
      () => this.memory.checkHeap('memory_heap', 300 * 1024 * 1024),
    ]);
    const status = result.status;
    if (status === 'ok') {
      this.logger.debug('Health check passed');
    } else {
      this.logger.warn(`Health check degraded — status: ${status}`);
    }
    return result;
  }
}"""

FILES["src/common/health/health.module.ts"] = r"""import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from '@common/health/health.controller';

@Module({
  imports: [TerminusModule],
  controllers: [HealthController],
})
export class HealthModule {}"""

# ─── Users ────────────────────────────────────────────────────────────────────

FILES["src/modules/users/entities/user.entity.ts"] = r"""import { Exclude, Expose } from 'class-transformer';
import { Column, Entity, Index } from 'typeorm';
import { AuditBaseEntity } from '@common/base/audit.base.entity';
import { UserRole } from '@common/enums/user-role.enum';
import { ApiProperty } from '@nestjs/swagger';

@Entity('users')
export class User extends AuditBaseEntity {
  @Expose()
  @ApiProperty({ example: 'user@example.com' })
  @Index()
  @Column({ name: 'email', type: 'varchar', length: 320, unique: true })
  email!: string;

  // FIX: @Exclude ensures password never leaks via ClassSerializerInterceptor
  @Exclude()
  @Column({ name: 'password', type: 'varchar', length: 255 })
  password!: string;

  @Expose()
  @ApiProperty({ enum: UserRole })
  @Column({
    name: 'role',
    type: 'enum',
    enum: UserRole,
    default: UserRole.STUDENT,
  })
  role!: UserRole;

  // FIX: never expose hashed refresh token
  @Exclude()
  @Column({
    name: 'hashed_refresh_token',
    type: 'varchar',
    length: 255,
    nullable: true,
  })
  hashedRefreshToken!: string | null;

  @Expose()
  @Column({ name: 'is_active', type: 'boolean', default: true })
  isActive!: boolean;
}"""

FILES["src/modules/users/users.service.ts"] = r"""import {
  ConflictException,
  Injectable,
  InternalServerErrorException,
  Logger,
  NotFoundException,
  UnauthorizedException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '@modules/users/entities/user.entity';
import { RegisterDto } from '@modules/auth/dto/register.dto';
import * as bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

/** Mask email for safe logging — avoids PII in log files */
function maskEmail(email: string): string {
  const [local, domain] = email.split('@');
  if (!local || !domain) return '***';
  return `${local[0]}***@${domain}`;
}

@Injectable()
export class UsersService {
  private readonly logger = new Logger(UsersService.name);

  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async create(registerDto: RegisterDto): Promise<User> {
    this.logger.debug(`Checking for existing account: ${maskEmail(registerDto.email)}`);

    const existing = await this.userRepository.findOne({
      where: { email: registerDto.email.toLowerCase() },
    });

    if (existing) {
      this.logger.warn(`Registration conflict — email already exists: ${maskEmail(registerDto.email)}`);
      throw new ConflictException('A user with this email already exists');
    }

    this.logger.debug('Hashing password');
    const hashedPassword = await bcrypt.hash(registerDto.password, SALT_ROUNDS);

    const user = this.userRepository.create({
      ...registerDto,
      email: registerDto.email.toLowerCase(),
      password: hashedPassword,
    });

    try {
      const saved = await this.userRepository.save(user);
      this.logger.log(`User created — userId: ${saved.id}, role: ${saved.role}`);
      return saved;
    } catch (error) {
      this.logger.error('Database error while creating user', error);
      throw new InternalServerErrorException('Failed to create user account');
    }
  }

  async findByEmail(email: string): Promise<User | null> {
    this.logger.debug(`Looking up user by email: ${maskEmail(email)}`);
    const user = await this.userRepository.findOne({
      where: { email: email.toLowerCase(), isActive: true },
    });
    if (!user) {
      this.logger.debug(`No active user found for: ${maskEmail(email)}`);
    }
    return user;
  }

  async findById(id: string): Promise<User> {
    this.logger.debug(`Looking up user by id: ${id}`);
    const user = await this.userRepository.findOne({
      where: { id, isActive: true },
    });

    if (!user) {
      this.logger.warn(`User not found or inactive — userId: ${id}`);
      throw new NotFoundException(`User not found`);
    }

    return user;
  }

  async updateHashedRefreshToken(
    userId: string,
    refreshToken: string | null,
  ): Promise<void> {
    let hashedRefreshToken: string | null = null;

    if (refreshToken !== null) {
      hashedRefreshToken = await bcrypt.hash(refreshToken, SALT_ROUNDS);
      this.logger.debug(`Refresh token stored — userId: ${userId}`);
    } else {
      this.logger.debug(`Refresh token cleared — userId: ${userId}`);
    }

    await this.userRepository.update(userId, { hashedRefreshToken });
  }

  async validateRefreshToken(
    userId: string,
    refreshToken: string,
  ): Promise<User> {
    this.logger.debug(`Validating refresh token — userId: ${userId}`);
    const user = await this.findById(userId);

    // FIX: generic error — prevents user-enumeration via specific messages
    if (!user.hashedRefreshToken) {
      this.logger.warn(`Refresh attempt with no stored token — userId: ${userId}`);
      throw new UnauthorizedException('Invalid or expired session');
    }

    const isValid = await bcrypt.compare(refreshToken, user.hashedRefreshToken);

    if (!isValid) {
      this.logger.warn(`Refresh token mismatch — userId: ${userId}, email: ${maskEmail(user.email)}`);
      throw new UnauthorizedException('Invalid or expired session');
    }

    this.logger.debug(`Refresh token valid — userId: ${userId}`);
    return user;
  }
}"""

FILES["src/modules/users/users.module.ts"] = r"""import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from '@modules/users/entities/user.entity';
import { UsersService } from '@modules/users/users.service';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}"""

# ─── Auth — DTOs ──────────────────────────────────────────────────────────────

FILES["src/modules/auth/dto/login.dto.ts"] = r"""import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';
import { Transform } from 'class-transformer';
import { ApiProperty } from '@nestjs/swagger';

export class LoginDto {
  @ApiProperty({ example: 'user@example.com' })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  @Transform(({ value }: { value: string }) => value?.toLowerCase().trim())
  email!: string;

  @ApiProperty({ example: 'P@ssw0rd!' })
  @IsString({ message: 'Password must be a string' })
  @IsNotEmpty({ message: 'Password is required' })
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  password!: string;
}"""

FILES["src/modules/auth/dto/register.dto.ts"] = r"""import {
  IsEmail,
  IsEnum,
  IsNotEmpty,
  IsOptional,
  IsString,
  Matches,
} from 'class-validator';
import { Transform } from 'class-transformer';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { UserRole } from '@common/enums/user-role.enum';

export class RegisterDto {
  @ApiProperty({ example: 'user@example.com' })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  @Transform(({ value }: { value: string }) => value?.toLowerCase().trim())
  email!: string;

  @ApiProperty({ example: 'P@ssw0rd!' })
  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  // FIX: length (8-72) enforced inside regex — eliminates the gap between
  // @MinLength/@MaxLength and the complexity check
  @Matches(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,72}$/,
    {
      message:
        'Password must be 8-72 characters and contain at least one uppercase letter, one lowercase letter, one number, and one special character (@$!%*?&)',
    },
  )
  password!: string;

  @ApiPropertyOptional({ enum: UserRole })
  @IsEnum(UserRole, {
    message: `Role must be one of: ${Object.values(UserRole).join(', ')}`,
  })
  @IsOptional()
  role?: UserRole;
}"""

FILES["src/modules/auth/dto/refresh-token.dto.ts"] = r"""import { IsNotEmpty, IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class RefreshTokenDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  refreshToken!: string;
}"""

# ─── Auth — Strategies ────────────────────────────────────────────────────────

FILES["src/modules/auth/strategies/jwt.strategy.ts"] = r"""import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { UsersService } from '@modules/users/users.service';
import { User } from '@modules/users/entities/user.entity';
import { UserRole } from '@common/enums/user-role.enum';

export interface JwtPayload {
  sub: string;
  email: string;
  role: UserRole;
  iat?: number;
  exp?: number;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
  constructor(
    private readonly configService: ConfigService,
    private readonly usersService: UsersService,
  ) {
    const secret = configService.get<string>('JWT_SECRET');
    if (!secret) {
      throw new Error('JWT_SECRET environment variable is not configured');
    }

    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: secret,
    });
  }

  async validate(payload: JwtPayload): Promise<User> {
    const user = await this.usersService.findById(payload.sub);

    if (!user || !user.isActive) {
      throw new UnauthorizedException('User not found or account is inactive');
    }

    return user;
  }
}"""

# FIX: dedicated refresh strategy — userId now comes from the verified token,
# not the request body (prevents user-controlled userId injection)
FILES["src/modules/auth/strategies/jwt-refresh.strategy.ts"] = r"""import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { Request } from 'express';
import { JwtPayload } from '@modules/auth/strategies/jwt.strategy';

export interface JwtRefreshPayload extends JwtPayload {
  refreshToken: string;
}

@Injectable()
export class JwtRefreshStrategy extends PassportStrategy(Strategy, 'jwt-refresh') {
  constructor(configService: ConfigService) {
    const secret = configService.get<string>('JWT_REFRESH_SECRET');
    if (!secret) {
      throw new Error('JWT_REFRESH_SECRET is not configured');
    }

    super({
      jwtFromRequest: ExtractJwt.fromBodyField('refreshToken'),
      ignoreExpiration: false,
      secretOrKey: secret,
      passReqToCallback: true,
    });
  }

  validate(req: Request, payload: JwtPayload): JwtRefreshPayload {
    const refreshToken = (req.body as { refreshToken?: string }).refreshToken;

    if (!refreshToken) {
      throw new UnauthorizedException('Refresh token missing');
    }

    return { ...payload, refreshToken };
  }
}"""

# ─── Auth — Service ───────────────────────────────────────────────────────────

FILES["src/modules/auth/auth.service.ts"] = r"""import {
  Injectable,
  Logger,
  UnauthorizedException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from '@modules/users/users.service';
import { LoginDto } from '@modules/auth/dto/login.dto';
import { RegisterDto } from '@modules/auth/dto/register.dto';
import { User } from '@modules/users/entities/user.entity';
import { JwtPayload } from '@modules/auth/strategies/jwt.strategy';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  async register(registerDto: RegisterDto): Promise<LoginResponse> {
    this.logger.debug('Creating new user account');
    const user = await this.usersService.create(registerDto);
    this.logger.log(`New account registered — userId: ${user.id}, role: ${user.role}`);

    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(user.id, tokens.refreshToken);
    this.logger.debug(`Initial tokens issued — userId: ${user.id}`);

    return { user, ...tokens };
  }

  async login(loginDto: LoginDto): Promise<LoginResponse> {
    this.logger.debug('Validating credentials');
    const user = await this.validateUserCredentials(
      loginDto.email,
      loginDto.password,
    );

    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(user.id, tokens.refreshToken);

    this.logger.log(`User authenticated — userId: ${user.id}, role: ${user.role}`);

    return { user, ...tokens };
  }

  async logout(userId: string): Promise<{ message: string }> {
    this.logger.debug(`Revoking refresh token — userId: ${userId}`);
    await this.usersService.updateHashedRefreshToken(userId, null);
    this.logger.log(`Session terminated — userId: ${userId}`);
    return { message: 'Logged out successfully' };
  }

  // FIX: userId sourced from verified JWT payload, not request body
  async refreshTokens(userId: string, refreshToken: string): Promise<AuthTokens> {
    this.logger.debug(`Rotating tokens — userId: ${userId}`);
    const user = await this.usersService.validateRefreshToken(userId, refreshToken);
    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(user.id, tokens.refreshToken);
    this.logger.log(`Tokens rotated — userId: ${userId}`);
    return tokens;
  }

  private async validateUserCredentials(
    email: string,
    password: string,
  ): Promise<User> {
    const user = await this.usersService.findByEmail(email);

    // FIX: constant-time compare even when user not found — prevent timing attack
    const dummyHash =
      '$2b$12$invalidhashfortimingprotectionxxxxxxxxxxxxxxxxxxxxxxxx';
    const isPasswordValid = await bcrypt.compare(
      password,
      user?.password ?? dummyHash,
    );

    if (!user || !isPasswordValid) {
      // log without revealing which field failed — no user enumeration
      this.logger.warn('Failed login attempt — invalid credentials');
      throw new UnauthorizedException('Invalid email or password');
    }

    if (!user.isActive) {
      this.logger.warn(`Login blocked — inactive account: ${user.id}`);
      throw new UnauthorizedException('Account is deactivated');
    }

    return user;
  }

  private async generateTokens(user: User): Promise<AuthTokens> {
    const payload: JwtPayload = {
      sub: user.id,
      email: user.email,
      role: user.role,
    };

    const jwtSecret = this.configService.get<string>('JWT_SECRET');
    const jwtRefreshSecret = this.configService.get<string>('JWT_REFRESH_SECRET');

    if (!jwtSecret || !jwtRefreshSecret) {
      this.logger.error('JWT secrets missing — check environment configuration');
      throw new Error('JWT secrets are not configured');
    }

    const [accessToken, refreshToken] = await Promise.all([
      this.jwtService.signAsync(payload, { secret: jwtSecret, expiresIn: '15m' }),
      this.jwtService.signAsync(payload, {
        secret: jwtRefreshSecret,
        expiresIn: '7d',
      }),
    ]);

    this.logger.debug(`Token pair generated — userId: ${user.id}`);
    return { accessToken, refreshToken };
  }
}"""

# ─── Auth — Controller ────────────────────────────────────────────────────────

FILES["src/modules/auth/auth.controller.ts"] = r"""import {
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  Logger,
  Post,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ApiBearerAuth, ApiTags } from '@nestjs/swagger';
import { Throttle } from '@nestjs/throttler';
import { AuthService } from '@modules/auth/auth.service';
import { LoginDto } from '@modules/auth/dto/login.dto';
import { RegisterDto } from '@modules/auth/dto/register.dto';
import { GetUser } from '@common/decorators/get-user.decorator';
import { JwtAuthGuard } from '@common/guards/jwt-auth.guard';
import { Public } from '@common/decorators/public.decorator';
import { User } from '@modules/users/entities/user.entity';
import { JwtRefreshPayload } from '@modules/auth/strategies/jwt-refresh.strategy';

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  private readonly logger = new Logger(AuthController.name);

  constructor(private readonly authService: AuthService) {}

  @Public()
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @Post('register')
  @HttpCode(HttpStatus.CREATED)
  async register(@Body() registerDto: RegisterDto) {
    this.logger.log('POST /auth/register — new registration attempt');
    const result = await this.authService.register(registerDto);
    this.logger.log(`POST /auth/register — account created: ${result.user.id}`);
    return result;
  }

  @Public()
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @Post('login')
  @HttpCode(HttpStatus.OK)
  async login(@Body() loginDto: LoginDto) {
    this.logger.log('POST /auth/login — login attempt');
    const result = await this.authService.login(loginDto);
    this.logger.log(`POST /auth/login — success: ${result.user.id}`);
    return result;
  }

  @ApiBearerAuth()
  @UseGuards(JwtAuthGuard)
  @Post('logout')
  @HttpCode(HttpStatus.OK)
  async logout(@GetUser() user: User) {
    this.logger.log(`POST /auth/logout — user: ${user.id}`);
    const result = await this.authService.logout(user.id);
    this.logger.log(`POST /auth/logout — session cleared: ${user.id}`);
    return result;
  }

  @Public()
  @UseGuards(AuthGuard('jwt-refresh'))
  @Post('refresh')
  @HttpCode(HttpStatus.OK)
  async refresh(@GetUser() payload: JwtRefreshPayload) {
    this.logger.log(`POST /auth/refresh — token refresh for user: ${payload.sub}`);
    const result = await this.authService.refreshTokens(payload.sub, payload.refreshToken);
    this.logger.log(`POST /auth/refresh — tokens rotated for user: ${payload.sub}`);
    return result;
  }
}"""

# ─── Auth — Module ────────────────────────────────────────────────────────────

FILES["src/modules/auth/auth.module.ts"] = r"""import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { AuthController } from '@modules/auth/auth.controller';
import { AuthService } from '@modules/auth/auth.service';
import { JwtStrategy } from '@modules/auth/strategies/jwt.strategy';
import { JwtRefreshStrategy } from '@modules/auth/strategies/jwt-refresh.strategy';
import { UsersModule } from '@modules/users/users.module';

@Module({
  imports: [
    PassportModule.register({ defaultStrategy: 'jwt' }),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        secret: configService.get<string>('JWT_SECRET'),
        signOptions: { expiresIn: '15m' },
      }),
    }),
    UsersModule,
  ],
  controllers: [AuthController],
  providers: [AuthService, JwtStrategy, JwtRefreshStrategy],
  exports: [AuthService, JwtModule],
})
export class AuthModule {}"""

# ─── App Module ───────────────────────────────────────────────────────────────

FILES["src/app.module.ts"] = r"""import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_FILTER, APP_GUARD, APP_INTERCEPTOR } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { WinstonModule } from 'nest-winston';
import { typeormConfig } from '@config/typeorm.config';
import { winstonConfig } from '@config/logger.config';
import { validate } from '@config/env.validation';
import { DatabaseModule } from '@database/database.module';
import { HttpExceptionFilter } from '@common/filters/http-exception.filter';
import { TransformInterceptor } from '@common/interceptors/transform.interceptor';
import { JwtAuthGuard } from '@common/guards/jwt-auth.guard';
import { RolesGuard } from '@common/guards/roles.guard';
import { HealthModule } from '@common/health/health.module';
import { AuthModule } from '@modules/auth/auth.module';
import { UsersModule } from '@modules/users/users.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
      load: [typeormConfig],
      envFilePath: ['.env.local', '.env'],
    }),
    // Winston logger — replaces NestJS built-in logger globally
    WinstonModule.forRoot(winstonConfig),
    // FIX: rate limiting — short burst + per-minute window
    ThrottlerModule.forRoot([
      { name: 'short', ttl: 1000, limit: 10 },
      { name: 'medium', ttl: 60000, limit: 100 },
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
export class AppModule {}"""

# ─── Main ─────────────────────────────────────────────────────────────────────

FILES["src/main.ts"] = r"""import { ClassSerializerInterceptor, Logger, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory, Reflector } from '@nestjs/core';
import { NestExpressApplication } from '@nestjs/platform-express';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppModule } from './app.module';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create<NestExpressApplication>(AppModule, {
    // FIX: buffer logs until Winston is ready — no lost bootstrap messages
    bufferLogs: true,
  });

  // FIX: replace NestJS built-in logger with Winston
  app.useLogger(app.get(WINSTON_MODULE_NEST_PROVIDER));

  const logger = new Logger('Bootstrap');
  const configService = app.get(ConfigService);
  const port = configService.get<number>('PORT', 3000);
  const nodeEnv = configService.get<string>('NODE_ENV', 'development');

  app.setGlobalPrefix('api/v1');
  app.set('trust proxy', 1);

  app.enableCors({
    origin: configService.get<string>('CORS_ORIGIN', '*'),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
  });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // FIX: strategy 'excludeAll' — only @Expose() fields are returned;
  // sensitive fields (@Exclude) never leak even without explicit decorator
  app.useGlobalInterceptors(
    new ClassSerializerInterceptor(app.get(Reflector), {
      strategy: 'excludeAll',
      excludeExtraneousValues: false,
    }),
  );

  // Swagger — only in non-production
  if (nodeEnv !== 'production') {
    const swaggerConfig = new DocumentBuilder()
      .setTitle('ProjectX API')
      .setDescription('Enterprise NestJS Starter')
      .setVersion('1.0')
      .addBearerAuth()
      .build();
    SwaggerModule.setup(
      'api/v1/docs',
      app,
      SwaggerModule.createDocument(app, swaggerConfig),
    );
    logger.log(`Swagger docs: http://localhost:${port}/api/v1/docs`);
  }

  app.enableShutdownHooks();

  await app.listen(port);

  logger.log(`Application running on: http://localhost:${port}/api/v1`);
  logger.log(`Environment: ${nodeEnv}`);
}

bootstrap().catch((err: unknown) => {
  const logger = new Logger('Bootstrap');
  logger.error('Failed to start application', err);
  process.exit(1);
});"""

FILES["create_project.py"] = open(__file__).read()

def create_zip(output_path="projectx-backend.zip"):
    print(f"Creating {output_path}...")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path, content in FILES.items():
            zf.writestr(f"projectx-backend/{rel_path}", content.strip() + "\n")
            print(f"  + {rel_path}")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\nDone! {output_path} ({size_kb:.1f} KB), {len(FILES)} files")

if __name__ == "__main__":
    create_zip("/mnt/user-data/outputs/projectx-backend.zip")
