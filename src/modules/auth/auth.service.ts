import { Injectable, Logger, UnauthorizedException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcrypt";
import { UsersService } from "@modules/users/users.service";
import { LoginDto } from "@modules/auth/dto/login.dto";
import { RegisterDto } from "@modules/auth/dto/register.dto";
import { User } from "@modules/users/entities/user.entity";
import { JwtPayload } from "@modules/auth/strategies/jwt.strategy";

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
    this.logger.debug("Creating new user account");
    const user = await this.usersService.create(registerDto);
    this.logger.log(
      `New account registered — userId: ${user.id}, role: ${user.role}`,
    );

    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(
      user.id,
      tokens.refreshToken,
    );
    this.logger.debug(`Initial tokens issued — userId: ${user.id}`);

    return { user, ...tokens };
  }

  async login(loginDto: LoginDto): Promise<LoginResponse> {
    this.logger.debug("Validating credentials");
    const user = await this.validateUserCredentials(
      loginDto.email,
      loginDto.password,
    );

    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(
      user.id,
      tokens.refreshToken,
    );

    this.logger.log(
      `User authenticated — userId: ${user.id}, role: ${user.role}`,
    );

    return { user, ...tokens };
  }

  async logout(userId: string): Promise<{ message: string }> {
    this.logger.debug(`Revoking refresh token — userId: ${userId}`);
    await this.usersService.updateHashedRefreshToken(userId, null);
    this.logger.log(`Session terminated — userId: ${userId}`);
    return { message: "Logged out successfully" };
  }

  // FIX: userId sourced from verified JWT payload, not request body
  async refreshTokens(
    userId: string,
    refreshToken: string,
  ): Promise<AuthTokens> {
    this.logger.debug(`Rotating tokens — userId: ${userId}`);
    const user = await this.usersService.validateRefreshToken(
      userId,
      refreshToken,
    );
    const tokens = await this.generateTokens(user);
    await this.usersService.updateHashedRefreshToken(
      user.id,
      tokens.refreshToken,
    );
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
      "$2b$12$invalidhashfortimingprotectionxxxxxxxxxxxxxxxxxxxxxxxx";
    const isPasswordValid = await bcrypt.compare(
      password,
      user?.password ?? dummyHash,
    );

    if (!user || !isPasswordValid) {
      // log without revealing which field failed — no user enumeration
      this.logger.warn("Failed login attempt — invalid credentials");
      throw new UnauthorizedException("Invalid email or password");
    }

    if (!user.isActive) {
      this.logger.warn(`Login blocked — inactive account: ${user.id}`);
      throw new UnauthorizedException("Account is deactivated");
    }

    return user;
  }

  private async generateTokens(user: User): Promise<AuthTokens> {
    const payload: JwtPayload = {
      sub: user.id,
      email: user.email,
      role: user.role,
    };

    const jwtSecret = this.configService.get<string>("JWT_SECRET");
    const jwtRefreshSecret =
      this.configService.get<string>("JWT_REFRESH_SECRET");

    if (!jwtSecret || !jwtRefreshSecret) {
      this.logger.error(
        "JWT secrets missing — check environment configuration",
      );
      throw new Error("JWT secrets are not configured");
    }

    const [accessToken, refreshToken] = await Promise.all([
      this.jwtService.signAsync(payload, {
        secret: jwtSecret,
        expiresIn: "15m",
      }),
      this.jwtService.signAsync(payload, {
        secret: jwtRefreshSecret,
        expiresIn: "7d",
      }),
    ]);

    this.logger.debug(`Token pair generated — userId: ${user.id}`);
    return { accessToken, refreshToken };
  }
}
