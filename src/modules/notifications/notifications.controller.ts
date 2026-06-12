import {
  Controller,
  Get,
  Patch,
  Param,
  ParseUUIDPipe,
  HttpCode,
  HttpStatus,
} from "@nestjs/common";
import { ApiBearerAuth, ApiTags } from "@nestjs/swagger";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Notification } from "./notification.entity";
import { GetUser } from "@common/decorators/get-user.decorator";
import { User } from "@modules/users/entities/user.entity";

@ApiTags("Notifications")
@ApiBearerAuth()
@Controller("notifications")
export class NotificationsController {
  constructor(
    @InjectRepository(Notification)
    private readonly repo: Repository<Notification>,
  ) {}

  @Get()
  findMine(@GetUser() user: User) {
    return this.repo.find({
      where: { userId: user.id },
      order: { createdDate: "DESC" },
      take: 30,
    });
  }

  @Patch(":id/read")
  @HttpCode(HttpStatus.OK)
  markRead(@Param("id", ParseUUIDPipe) id: string, @GetUser() user: User) {
    return this.repo.update({ id, userId: user.id }, { isRead: true });
  }

  @Patch("read-all")
  @HttpCode(HttpStatus.OK)
  markAllRead(@GetUser() user: User) {
    return this.repo.update(
      { userId: user.id, isRead: false },
      { isRead: true },
    );
  }
}
