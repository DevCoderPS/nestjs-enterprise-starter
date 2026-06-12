import { Column, Entity } from "typeorm";
import { AuditBaseEntity } from "@common/base/audit.base.entity";

export enum NotificationType {
  INFO = "INFO",
  WARNING = "WARNING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

@Entity("notifications")
export class Notification extends AuditBaseEntity {
  @Column({ name: "user_id", type: "uuid" })
  userId!: string;

  @Column({ name: "title", type: "varchar", length: 255 })
  title!: string;

  @Column({ name: "message", type: "text" })
  message!: string;

  @Column({
    name: "type",
    type: "enum",
    enum: NotificationType,
    default: NotificationType.INFO,
  })
  type!: NotificationType;

  @Column({ name: "is_read", type: "boolean", default: false })
  isRead!: boolean;
}
