import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { MulterModule } from "@nestjs/platform-express";
import { memoryStorage } from "multer";
import { User } from "@modules/users/entities/user.entity";
import { UsersService } from "@modules/users/users.service";
import { UsersAdminService } from "@modules/users/users-admin.service";
import { AvatarService } from "@modules/users/avatar.service";
import { UsersController } from "@modules/users/users.controller";

@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    // Store file in memory so we can pass buffer to AvatarService
    MulterModule.register({ storage: memoryStorage() }),
  ],
  controllers: [UsersController],
  providers: [UsersService, UsersAdminService, AvatarService],
  exports: [UsersService],
})
export class UsersModule {}
