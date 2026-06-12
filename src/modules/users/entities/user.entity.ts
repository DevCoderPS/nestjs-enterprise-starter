import { Exclude, Expose } from "class-transformer";
import { Column, Entity, Index } from "typeorm";
import { AuditBaseEntity } from "@common/base/audit.base.entity";
import { UserRole } from "@common/enums/user-role.enum";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

@Entity("users")
export class User extends AuditBaseEntity {
  @Expose()
  @ApiProperty({ example: "user@example.com" })
  @Index()
  @Column({ name: "email", type: "varchar", length: 320, unique: true })
  email!: string;

  @Exclude()
  @Column({ name: "password", type: "varchar", length: 255 })
  password!: string;

  @Expose()
  @ApiProperty({ enum: UserRole })
  @Column({
    name: "role",
    type: "enum",
    enum: UserRole,
    default: UserRole.USER,
  })
  role!: UserRole;

  @Exclude()
  @Column({
    name: "hashed_refresh_token",
    type: "varchar",
    length: 255,
    nullable: true,
  })
  hashedRefreshToken!: string | null;

  @Expose()
  @Column({ name: "is_active", type: "boolean", default: true })
  isActive!: boolean;

  // ── Profile fields ──────────────────────────────────────────────────────────
  @Expose()
  @ApiPropertyOptional({ example: "John" })
  @Column({ name: "first_name", type: "varchar", length: 100, nullable: true })
  firstName!: string | null;

  @Expose()
  @ApiPropertyOptional({ example: "Doe" })
  @Column({ name: "last_name", type: "varchar", length: 100, nullable: true })
  lastName!: string | null;

  @Expose()
  @ApiPropertyOptional({ example: "+959123456789" })
  @Column({ name: "phone", type: "varchar", length: 30, nullable: true })
  phone!: string | null;

  @Expose()
  @ApiPropertyOptional({ example: "Software Engineer" })
  @Column({ name: "job_title", type: "varchar", length: 150, nullable: true })
  jobTitle!: string | null;

  @Expose()
  @ApiPropertyOptional({ example: "Engineering" })
  @Column({ name: "department", type: "varchar", length: 100, nullable: true })
  department!: string | null;

  // stores relative path e.g. "uploads/avatars/uuid.jpg"
  @Expose()
  @ApiPropertyOptional()
  @Column({ name: "avatar_path", type: "varchar", length: 500, nullable: true })
  avatarPath!: string | null;

  @Expose()
  @ApiPropertyOptional()
  @Column({ name: "last_login_at", type: "timestamptz", nullable: true })
  lastLoginAt!: Date | null;
}
