import { Exclude, Expose } from "class-transformer";
import {
  Column,
  CreateDateColumn,
  DeleteDateColumn,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from "typeorm";

export abstract class AuditBaseEntity {
  @Expose()
  @PrimaryGeneratedColumn("uuid")
  id!: string;

  @Expose()
  @CreateDateColumn({ name: "created_date", type: "timestamptz" })
  createdDate!: Date;

  @Column({ name: "created_by", type: "varchar", length: 255, nullable: true })
  createdBy!: string | null;

  @Expose()
  @UpdateDateColumn({ name: "updated_date", type: "timestamptz" })
  updatedDate!: Date;

  @Column({ name: "updated_by", type: "varchar", length: 255, nullable: true })
  updatedBy!: string | null;

  @Exclude()
  @DeleteDateColumn({
    name: "deleted_date",
    type: "timestamptz",
    nullable: true,
  })
  deletedDate!: Date | null;
}
