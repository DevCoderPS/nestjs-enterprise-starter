import {
  ConflictException,
  ForbiddenException,
  Injectable,
  InternalServerErrorException,
  Logger,
  NotFoundException,
} from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Between, ILike, Repository } from "typeorm";
import * as bcrypt from "bcrypt";
import { User } from "@modules/users/entities/user.entity";
import { CreateUserDto } from "@modules/users/dto/create-user.dto";
import { UpdateUserDto } from "@modules/users/dto/update-user.dto";
import { ListUsersDto } from "@modules/users/dto/list-users.dto";
import { AvatarService } from "@modules/users/avatar.service";
import { UserRole } from "@common/enums/user-role.enum";

const SALT = 12;

export interface PaginatedUsers {
  data: User[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

@Injectable()
export class UsersAdminService {
  private readonly logger = new Logger(UsersAdminService.name);

  constructor(
    @InjectRepository(User) private readonly repo: Repository<User>,
    private readonly avatarService: AvatarService,
  ) {}

  // ── CREATE ─────────────────────────────────────────────────────────────────
  async create(
    dto: CreateUserDto,
    actor: User,
    avatarBuffer?: Buffer,
    avatarMime?: string,
    avatarOriginal?: string,
  ): Promise<User> {
    if (
      dto.role &&
      dto.role !== UserRole.USER &&
      actor.role !== UserRole.SUPER_ADMIN
    )
      throw new ForbiddenException(
        "Only SUPER_ADMIN can create elevated roles",
      );

    const existing = await this.repo.findOne({
      where: { email: dto.email },
      withDeleted: true,
    });
    if (existing) throw new ConflictException("Email already exists");

    let avatarPath: string | undefined;
    if (avatarBuffer && avatarMime && avatarOriginal) {
      avatarPath = await this.avatarService.save(
        avatarBuffer,
        avatarMime,
        avatarOriginal,
      );
    }

    const user = this.repo.create({
      email: dto.email,
      password: await bcrypt.hash(dto.password, SALT),
      role: dto.role ?? UserRole.USER,
      firstName: dto.firstName,
      lastName: dto.lastName,
      phone: dto.phone,
      jobTitle: dto.jobTitle,
      department: dto.department,
      avatarPath: avatarPath ?? null,
      createdBy: actor.id,
      updatedBy: actor.id,
    });

    try {
      const saved = await this.repo.save(user);
      this.logger.log(`User created: ${saved.id} by ${actor.id}`);
      return saved;
    } catch {
      if (avatarPath) this.avatarService.delete(avatarPath);
      throw new InternalServerErrorException("Failed to create user");
    }
  }

  // ── LIST ───────────────────────────────────────────────────────────────────
  async findAll(q: ListUsersDto): Promise<PaginatedUsers> {
    const { page = 1, limit = 20, email, isActive, joinedFrom, joinedTo } = q;
    const skip = (page - 1) * limit;

    const where: Record<string, unknown> = {};
    if (email) where["email"] = ILike(`%${email}%`);
    if (isActive !== undefined) where["isActive"] = isActive;
    if (joinedFrom || joinedTo) {
      where["createdDate"] = Between(
        joinedFrom ? new Date(joinedFrom) : new Date("2000-01-01"),
        joinedTo ? new Date(joinedTo) : new Date(),
      );
    }

    const [data, total] = await this.repo.findAndCount({
      where,
      order: { createdDate: "DESC" },
      skip,
      take: limit,
    });

    return { data, total, page, limit, totalPages: Math.ceil(total / limit) };
  }

  // ── GET ONE ────────────────────────────────────────────────────────────────
  async findOne(id: string): Promise<User> {
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return user;
  }

  // ── UPDATE ─────────────────────────────────────────────────────────────────
  async update(
    id: string,
    dto: UpdateUserDto,
    actor: User,
    avatarBuffer?: Buffer,
    avatarMime?: string,
    avatarOriginal?: string,
  ): Promise<User> {
    const user = await this.findOne(id);

    if (
      actor.role === UserRole.ADMIN &&
      (dto.role !== undefined || dto.password !== undefined)
    )
      throw new ForbiddenException(
        "ADMINs may only update isActive and profile fields",
      );
    if (
      user.role === UserRole.SUPER_ADMIN &&
      actor.role !== UserRole.SUPER_ADMIN
    )
      throw new ForbiddenException("Cannot modify a SUPER_ADMIN account");
    if (actor.id === id && dto.role && dto.role !== actor.role)
      throw new ForbiddenException("You cannot change your own role");

    let newAvatarPath = user.avatarPath;
    if (avatarBuffer && avatarMime && avatarOriginal) {
      newAvatarPath = await this.avatarService.save(
        avatarBuffer,
        avatarMime,
        avatarOriginal,
      );
      this.avatarService.delete(user.avatarPath);
    }

    const patch: Partial<User> = {
      updatedBy: actor.id,
      avatarPath: newAvatarPath,
    };
    if (dto.role !== undefined) patch.role = dto.role;
    if (dto.isActive !== undefined) patch.isActive = dto.isActive;
    if (dto.password !== undefined)
      patch.password = await bcrypt.hash(dto.password, SALT);
    if (dto.firstName !== undefined) patch.firstName = dto.firstName;
    if (dto.lastName !== undefined) patch.lastName = dto.lastName;
    if (dto.phone !== undefined) patch.phone = dto.phone;
    if (dto.jobTitle !== undefined) patch.jobTitle = dto.jobTitle;
    if (dto.department !== undefined) patch.department = dto.department;

    await this.repo.update(id, patch);
    this.logger.log(`User ${id} updated by ${actor.id}`);
    return this.findOne(id);
  }

  // ── DELETE ─────────────────────────────────────────────────────────────────
  async remove(id: string, actor: User): Promise<{ message: string }> {
    const user = await this.findOne(id);
    if (user.id === actor.id)
      throw new ForbiddenException("You cannot delete your own account");
    if (user.role === UserRole.SUPER_ADMIN)
      throw new ForbiddenException("Cannot delete a SUPER_ADMIN account");

    this.avatarService.delete(user.avatarPath);
    await this.repo.softDelete(id);
    this.logger.log(`User ${id} deleted by ${actor.id}`);
    return { message: `User ${id} deleted` };
  }
}
