import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Logger,
  Param,
  ParseUUIDPipe,
  Patch,
  Post,
  Query,
  UploadedFile,
  UseInterceptors,
} from "@nestjs/common";
import { FileInterceptor } from "@nestjs/platform-express";
import { ApiBearerAuth, ApiConsumes, ApiTags } from "@nestjs/swagger";
import { UsersAdminService } from "@modules/users/users-admin.service";
import { CreateUserDto } from "@modules/users/dto/create-user.dto";
import { UpdateUserDto } from "@modules/users/dto/update-user.dto";
import { ListUsersDto } from "@modules/users/dto/list-users.dto";
import { Roles } from "@common/decorators/roles.decorator";
import { GetUser } from "@common/decorators/get-user.decorator";
import { UserRole } from "@common/enums/user-role.enum";
import { User } from "@modules/users/entities/user.entity";

interface MulterFile {
  buffer: Buffer;
  mimetype: string;
  originalname: string;
}

@ApiTags("Users")
@ApiBearerAuth()
@Controller("users")
export class UsersController {
  private readonly logger = new Logger(UsersController.name);

  constructor(private readonly svc: UsersAdminService) {}

  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiConsumes("multipart/form-data")
  @UseInterceptors(FileInterceptor("avatar"))
  create(
    @Body() dto: CreateUserDto,
    @GetUser() actor: User,
    @UploadedFile() avatar?: MulterFile,
  ) {
    return this.svc.create(
      dto,
      actor,
      avatar?.buffer,
      avatar?.mimetype,
      avatar?.originalname,
    );
  }

  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Get()
  findAll(@Query() query: ListUsersDto) {
    return this.svc.findAll(query);
  }

  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Get(":id")
  findOne(@Param("id", ParseUUIDPipe) id: string) {
    return this.svc.findOne(id);
  }

  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Patch(":id")
  @ApiConsumes("multipart/form-data")
  @UseInterceptors(FileInterceptor("avatar"))
  update(
    @Param("id", ParseUUIDPipe) id: string,
    @Body() dto: UpdateUserDto,
    @GetUser() actor: User,
    @UploadedFile() avatar?: MulterFile,
  ) {
    return this.svc.update(
      id,
      dto,
      actor,
      avatar?.buffer,
      avatar?.mimetype,
      avatar?.originalname,
    );
  }

  @Roles(UserRole.SUPER_ADMIN)
  @Delete(":id")
  @HttpCode(HttpStatus.OK)
  remove(@Param("id", ParseUUIDPipe) id: string, @GetUser() actor: User) {
    return this.svc.remove(id, actor);
  }
}
