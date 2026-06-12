import {
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  Logger,
  Post,
  UseGuards,
} from "@nestjs/common";
import { AuthGuard } from "@nestjs/passport";
import { ApiBearerAuth, ApiTags } from "@nestjs/swagger";
import { Throttle } from "@nestjs/throttler";
import { AuthService } from "@modules/auth/auth.service";
import { LoginDto } from "@modules/auth/dto/login.dto";
import { RegisterDto } from "@modules/auth/dto/register.dto";
import { GetUser } from "@common/decorators/get-user.decorator";
import { JwtAuthGuard } from "@common/guards/jwt-auth.guard";
import { Public } from "@common/decorators/public.decorator";
import { User } from "@modules/users/entities/user.entity";
import { JwtRefreshPayload } from "@modules/auth/strategies/jwt-refresh.strategy";

@ApiTags("Auth")
@Controller("auth")
export class AuthController {
  private readonly logger = new Logger(AuthController.name);

  constructor(private readonly authService: AuthService) {}

  @Public()
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @Post("register")
  @HttpCode(HttpStatus.CREATED)
  async register(@Body() registerDto: RegisterDto) {
    this.logger.log("POST /auth/register — new registration attempt");
    const result = await this.authService.register(registerDto);
    this.logger.log(`POST /auth/register — account created: ${result.user.id}`);
    return result;
  }

  @Public()
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @Post("login")
  @HttpCode(HttpStatus.OK)
  async login(@Body() loginDto: LoginDto) {
    this.logger.log("POST /auth/login — login attempt");
    const result = await this.authService.login(loginDto);
    this.logger.log(`POST /auth/login — success: ${result.user.id}`);
    return result;
  }

  @ApiBearerAuth()
  @UseGuards(JwtAuthGuard)
  @Post("logout")
  @HttpCode(HttpStatus.OK)
  async logout(@GetUser() user: User) {
    this.logger.log(`POST /auth/logout — user: ${user.id}`);
    const result = await this.authService.logout(user.id);
    this.logger.log(`POST /auth/logout — session cleared: ${user.id}`);
    return result;
  }

  @Public()
  @UseGuards(AuthGuard("jwt-refresh"))
  @Post("refresh")
  @HttpCode(HttpStatus.OK)
  async refresh(@GetUser() payload: JwtRefreshPayload) {
    this.logger.log(
      `POST /auth/refresh — token refresh for user: ${payload.sub}`,
    );
    const result = await this.authService.refreshTokens(
      payload.sub,
      payload.refreshToken,
    );
    this.logger.log(
      `POST /auth/refresh — tokens rotated for user: ${payload.sub}`,
    );
    return result;
  }
}
