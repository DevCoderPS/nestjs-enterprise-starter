import {
  IsBoolean,
  IsDateString,
  IsInt,
  IsOptional,
  IsString,
  Max,
  Min,
} from "class-validator";
import { Transform } from "class-transformer";
import { ApiPropertyOptional } from "@nestjs/swagger";

export class ListUsersDto {
  @ApiPropertyOptional({ default: 1 })
  @IsInt()
  @Min(1)
  @IsOptional()
  @Transform(({ value }: { value: string }) => parseInt(value, 10))
  page?: number = 1;

  @ApiPropertyOptional({ default: 20 })
  @IsInt()
  @Min(1)
  @Max(100)
  @IsOptional()
  @Transform(({ value }: { value: string }) => parseInt(value, 10))
  limit?: number = 20;

  /** Email partial match */
  @ApiPropertyOptional()
  @IsString()
  @IsOptional()
  email?: string;

  /** true = active only, false = inactive only */
  @ApiPropertyOptional()
  @IsBoolean()
  @IsOptional()
  @Transform(({ value }: { value: string }) => {
    if (value === "true") return true;
    if (value === "false") return false;
    return undefined;
  })
  isActive?: boolean;

  /** joined from (ISO date) */
  @ApiPropertyOptional()
  @IsDateString()
  @IsOptional()
  joinedFrom?: string;

  /** joined to (ISO date) */
  @ApiPropertyOptional()
  @IsDateString()
  @IsOptional()
  joinedTo?: string;
}
