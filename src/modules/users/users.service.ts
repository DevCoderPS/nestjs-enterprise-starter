import {
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
}
