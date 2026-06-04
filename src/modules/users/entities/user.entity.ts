import { Exclude, Expose } from 'class-transformer';
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
    default: UserRole.USER,
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
}
