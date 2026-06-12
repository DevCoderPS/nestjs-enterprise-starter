import {
  IsEmail,
  IsEnum,
  IsNotEmpty,
  IsOptional,
  IsString,
  Matches,
} from "class-validator";
import { Transform } from "class-transformer";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { UserRole } from "@common/enums/user-role.enum";

export class RegisterDto {
  @ApiProperty({ example: "user@example.com" })
  @IsEmail({}, { message: "Please provide a valid email address" })
  @IsNotEmpty({ message: "Email is required" })
  @Transform(({ value }: { value: string }) => value?.toLowerCase().trim())
  email!: string;

  @ApiProperty({ example: "P@ssw0rd!" })
  @IsString()
  @IsNotEmpty({ message: "Password is required" })
  // FIX: length (8-72) enforced inside regex — eliminates the gap between
  // @MinLength/@MaxLength and the complexity check
  @Matches(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,72}$/,
    {
      message:
        "Password must be 8-72 characters and contain at least one uppercase letter, one lowercase letter, one number, and one special character (@$!%*?&)",
    },
  )
  password!: string;

  @ApiPropertyOptional({ enum: UserRole })
  @IsEnum(UserRole, {
    message: `Role must be one of: ${Object.values(UserRole).join(", ")}`,
  })
  @IsOptional()
  role?: UserRole;
}
